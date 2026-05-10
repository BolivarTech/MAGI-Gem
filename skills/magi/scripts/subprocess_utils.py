import os
from typing import Any


def format_stderr_excerpt(stderr_bytes: bytes) -> str:
    if not stderr_bytes:
        return ""
    return "\nStderr:\n" + stderr_bytes.decode("utf-8", errors="replace")[-500:]


async def reap_and_drain_stderr(proc: Any) -> bytes:
    # Minimal version
    return b""


def write_stderr_log(output_dir: str, agent_name: str, stderr: bytes) -> None:
    path = os.path.join(output_dir, f"{agent_name}.stderr.log")
    with open(path, "wb") as f:
        f.write(stderr)
