# Author: Julian Bolivar
# Version: 1.0.0
# Date: 2026-04-01
"""Tests for run_magi.py — async Python orchestrator."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import patch
from pathlib import Path

import pytest


class TestParseArgs:
    """Verify CLI argument parsing."""

    def test_minimal_args(self) -> None:
        from run_magi import parse_args

        args = parse_args(["code-review", "input.py"])
        assert args.mode == "code-review"
        assert args.input == "input.py"
        assert args.timeout == 900
        assert args.output_dir is None

    def test_custom_timeout(self) -> None:
        from run_magi import parse_args

        args = parse_args(["analysis", "file.txt", "--timeout", "60"])
        assert args.timeout == 60

    def test_custom_output_dir(self) -> None:
        from run_magi import parse_args

        args = parse_args(["design", "spec.md", "--output-dir", "/tmp/out"])
        assert args.output_dir == "/tmp/out"

    def test_invalid_mode_rejected(self) -> None:
        from run_magi import parse_args

        with pytest.raises(SystemExit):
            parse_args(["invalid-mode", "input.py"])

    def test_all_valid_modes(self) -> None:
        from run_magi import parse_args

        for mode in ("code-review", "design", "analysis"):
            args = parse_args([mode, "input.py"])
            assert args.mode == mode

    def test_default_model_mapping(self) -> None:
        """Verify that mode defaults are correctly mapped in models.py."""
        from run_magi import parse_args
        from models import MODE_DEFAULT_MODELS

        for mode, model in MODE_DEFAULT_MODELS.items():
            args = parse_args([mode, "input.py"])
            assert args.model == model

    def test_explicit_model_overrides_mode_default(self) -> None:
        from run_magi import parse_args

        args = parse_args(["analysis", "input.txt", "--model", "flash"])
        assert args.model == "flash"

    def test_invalid_model_rejected(self) -> None:
        from run_magi import parse_args

        with pytest.raises(SystemExit):
            parse_args(["code-review", "input.py", "--model", "gpt4"])

    def test_keep_runs_default(self) -> None:
        from run_magi import MAX_HISTORY_RUNS, parse_args

        args = parse_args(["code-review", "input.py"])
        assert args.keep_runs == MAX_HISTORY_RUNS

    def test_keep_runs_zero_rejected(self) -> None:
        from run_magi import parse_args

        with pytest.raises(SystemExit):
            parse_args(["code-review", "input.py", "--keep-runs", "0"])


class TestRunOrchestrator:
    """Verify full orchestration with mocked agents."""

    @pytest.mark.asyncio
    async def test_all_three_agents_success(self, tmp_path: Path) -> None:
        from run_magi import run_orchestrator

        agent_results: Dict[str, Dict[str, Any]] = {}
        for name in ("melchior", "balthasar", "caspar"):
            agent_results[name] = {
                "agent": name,
                "verdict": "approve",
                "confidence": 0.9,
                "summary": f"{name} OK",
                "reasoning": "Fine",
                "findings": [],
                "recommendation": "Merge",
            }

        async def mock_launch(
            agent_name: str,
            agents_dir: str,
            prompt: str,
            output_dir: str,
            timeout: int,
            model: str = "pro",
        ) -> Dict[str, Any]:
            return agent_results[agent_name]

        with patch("run_magi.launch_agent", side_effect=mock_launch):
            result = await run_orchestrator(
                agents_dir=str(tmp_path),
                prompt="test",
                output_dir=str(tmp_path),
                timeout=300,
            )
            assert result["consensus"]["consensus"] == "STRONG GO"
            assert result.get("degraded") is not True
            assert len(result["agents"]) == 3

    @pytest.mark.asyncio
    async def test_one_agent_fails_degraded_mode(self, tmp_path: Path) -> None:
        from run_magi import run_orchestrator

        async def mock_launch(
            agent_name: str,
            agents_dir: str,
            prompt: str,
            output_dir: str,
            timeout: int,
            model: str = "pro",
        ) -> Dict[str, Any]:
            if agent_name == "caspar":
                raise TimeoutError(f"Agent {agent_name} timed out")
            return {
                "agent": agent_name,
                "verdict": "approve",
                "confidence": 0.85,
                "summary": "OK",
                "reasoning": "Fine",
                "findings": [],
                "recommendation": "Merge",
            }

        with patch("run_magi.launch_agent", side_effect=mock_launch):
            result = await run_orchestrator(
                agents_dir=str(tmp_path),
                prompt="test",
                output_dir=str(tmp_path),
                timeout=300,
            )
            assert result["degraded"] is True
            assert "caspar" in result["failed_agents"]
            assert len(result["agents"]) == 2
