#!/usr/bin/env python3
# Ported MAGI Orchestrator for Gemini CLI v0.0.1
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from typing import Any

from models import MODE_DEFAULT_MODELS, MODEL_IDS, VALID_MODELS, resolve_model
from parse_agent_output import parse_agent_output as parse_raw_output
from status_display import StatusDisplay
from stderr_shim import _buffered_stderr_while
from synthesize import (
    determine_consensus,
    format_report,
    load_agent_output,
)
from subprocess_utils import (
    reap_and_drain_stderr as _reap_and_drain_stderr,
    write_stderr_log as _write_stderr_log,
)
from temp_dirs import (
    MAGI_DIR_PREFIX,
    cleanup_old_runs,
    create_output_dir,
)
from validate import MAX_INPUT_FILE_SIZE, ValidationError

__all__ = [
    "MAGI_DIR_PREFIX",
    "MODEL_IDS",
    "VALID_MODELS",
    "cleanup_old_runs",
    "create_output_dir",
    "resolve_model",
]

AGENTS = ("melchior", "balthasar", "caspar")
MAX_HISTORY_RUNS = 5
VALID_MODES = ("code-review", "design", "analysis")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MAGI Orchestrator (Gemini Edition)")
    parser.add_argument("mode", choices=VALID_MODES, help="Analysis mode")
    parser.add_argument("input", help="Path to file or inline text to analyze")
    parser.add_argument(
        "--timeout", type=int, default=900, help="Per-agent timeout in seconds"
    )
    parser.add_argument("--output-dir", help="Directory for agent outputs")
    parser.add_argument(
        "--model",
        choices=VALID_MODELS,
        default=None,
        help="LLM model (mapped to Gemini)",
    )
    parser.add_argument(
        "--keep-runs", type=int, default=MAX_HISTORY_RUNS, help="Temp dir cleanup"
    )
    parser.add_argument(
        "--no-status",
        dest="show_status",
        action="store_false",
        help="Disable status display",
    )
    parser.set_defaults(show_status=True)
    args = parser.parse_args(argv)
    if args.keep_runs == 0:
        parser.error("--keep-runs 0 is ambiguous.")
    if args.model is None:
        args.model = MODE_DEFAULT_MODELS[args.mode]
    return args


async def launch_agent(
    agent_name: str,
    agents_dir: str,
    prompt: str,
    output_dir: str,
    timeout: int,
    model: str = "opus",
) -> dict[str, Any]:
    system_prompt_file = os.path.join(agents_dir, f"{agent_name}.md")
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_content = f.read()

    # Load JSON schema for prompt injection
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, "schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        json_schema = f.read()

    # Gemini 1:1 strategy: Prepend system prompt and schema to user prompt
    full_payload = (
        f"{system_content}\n\n"
        f"STRICT OUTPUT FORMAT:\n"
        f"Your response MUST be a valid JSON object strictly following this schema:\n"
        f"{json_schema}\n\n"
        f"USER PROMPT:\n{prompt}"
    )

    raw_file = os.path.join(output_dir, f"{agent_name}.raw.json")
    parsed_file = os.path.join(output_dir, f"{agent_name}.json")

    # Call 'gemini' with standard json output and specific model
    model_id = resolve_model(model)
    cmd = (
        f'gemini --model "{model_id}" '
        f'-p "Respond following the provided instructions and schema." '
        f'--output-format json -'
    )
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=full_payload.encode("utf-8")), timeout=timeout
        )
    except asyncio.TimeoutError:
        stderr_buffered = await _reap_and_drain_stderr(proc)
        _write_stderr_log(output_dir, agent_name, stderr_buffered)
        raise TimeoutError(f"Agent '{agent_name}' timed out after {timeout}s") from None

    with open(raw_file, "wb") as f:
        f.write(stdout)

    _write_stderr_log(output_dir, agent_name, stderr)

    if proc.returncode != 0:
        stderr_text = (
            stderr.decode("utf-8", errors="replace").strip() if stderr else "no stderr"
        )
        raise RuntimeError(
            f"Agent '{agent_name}' exited with code {proc.returncode}: {stderr_text}"
        )

    parse_raw_output(raw_file, parsed_file)
    return load_agent_output(parsed_file)


# Include _DisplayLogGate, _safe_display_update, _build_retry_prompt, _load_input_content, run_orchestrator, etc.
# (Logic remains largely the same as the fetched version, but using launch_agent modified for Gemini)


class _DisplayLogGate:
    __slots__ = ("_logged",)

    def __init__(self) -> None:
        self._logged: bool = False

    def emit_once(self, exc: BaseException) -> None:
        if self._logged:
            return
        self._logged = True
        print(f"[!] WARNING: status display update failed ({exc!r})", file=sys.stderr)


def _safe_display_update(
    display: StatusDisplay | None, name: str, state: str, log_gate: _DisplayLogGate
) -> None:
    if display is None:
        return
    try:
        display.update(name, state)
    except BaseException as exc:
        log_gate.emit_once(exc)


def _build_retry_prompt(
    original_prompt: str, error: ValidationError | json.JSONDecodeError
) -> str:
    return f"{original_prompt}\n\n---RETRY-FEEDBACK---\nYour previous response was rejected: {error}\nRe-emit as valid JSON."


def _load_input_content(input_arg: str) -> tuple[str, str]:
    if os.path.isfile(input_arg):
        file_size = os.path.getsize(input_arg)
        if file_size > MAX_INPUT_FILE_SIZE:
            raise ValueError(f"Input file {input_arg} too large.")
        with open(input_arg, encoding="utf-8", errors="replace") as f:
            return f.read(), f"File: {input_arg}"
    return input_arg, "Inline input"


async def run_orchestrator(
    agents_dir: str,
    prompt: str,
    output_dir: str,
    timeout: int,
    model: str = "opus",
    *,
    show_status: bool = True,
) -> dict[str, Any]:
    successful: list[dict[str, Any]] = []
    failed: list[str] = []
    retried: set[str] = set()
    log_gate = _DisplayLogGate()
    display: StatusDisplay | None = (
        StatusDisplay(list(AGENTS), stream=sys.stderr) if show_status else None
    )

    async def tracked_launch(name: str) -> dict[str, Any]:
        _safe_display_update(display, name, "running", log_gate)
        try:
            try:
                result = await launch_agent(
                    name, agents_dir, prompt, output_dir, timeout, model
                )
            except (ValidationError, json.JSONDecodeError) as err:
                retried.add(name)
                _safe_display_update(display, name, "retrying", log_gate)
                result = await launch_agent(
                    name,
                    agents_dir,
                    _build_retry_prompt(prompt, err),
                    output_dir,
                    timeout,
                    model,
                )
        except (asyncio.TimeoutError, TimeoutError):
            _safe_display_update(display, name, "timeout", log_gate)
            raise
        except BaseException:
            _safe_display_update(display, name, "failed", log_gate)
            raise
        _safe_display_update(display, name, "success", log_gate)
        return result

    tasks = {name: tracked_launch(name) for name in AGENTS}
    if display:
        await display.start()
    with _buffered_stderr_while(active=display is not None):
        try:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        finally:
            if display:
                await display.stop()

    for name, result in zip(tasks.keys(), results):
        if isinstance(result, BaseException):
            if not isinstance(result, (Exception, asyncio.CancelledError)):
                raise result
            print(f"[!] WARNING: Agent '{name}' failed ({result})", file=sys.stderr)
            failed.append(name)
        else:
            successful.append(result)

    if len(successful) < 2:
        raise RuntimeError(f"Only {len(successful)} agent(s) succeeded.")

    consensus = determine_consensus(successful)
    report: dict[str, Any] = {"agents": successful, "consensus": consensus}
    if failed:
        report["degraded"] = True
        report["failed_agents"] = failed
    if retried:
        report["retried_agents"] = sorted(retried)
    return report


def main() -> None:
    args = parse_args()
    try:
        input_content, input_label = _load_input_content(args.input)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    prompt = f"MODE: {args.mode}\nCONTEXT ({input_label}):\n\n{input_content}"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    agents_dir = os.path.join(skill_dir, "agents")

    # Hard prerequisite check for 'gemini' instead of 'claude'
    if not shutil.which("gemini"):
        print("ERROR: 'gemini' CLI not found in PATH", file=sys.stderr)
        sys.exit(1)

    output_dir = create_output_dir(args.output_dir)
    print("+==================================================+")
    print("|          MAGI SYSTEM -- INITIALIZING (GEMINI)      |")
    print("+==================================================+")
    print(f"|  Mode: {args.mode}")
    print(f"|  Output: {output_dir}")
    print("+==================================================+")

    try:
        report = asyncio.run(
            run_orchestrator(
                agents_dir,
                prompt,
                output_dir,
                args.timeout,
                args.model,
                show_status=args.show_status,
            )
        )
    except BaseException:
        raise

    print(format_report(report["agents"], report["consensus"]))
    report_path = os.path.join(output_dir, "magi-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    main()
