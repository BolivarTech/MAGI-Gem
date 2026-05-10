# Test cases for skills/magi/scripts/validate.py

import json
import pytest
from pathlib import Path
from validate import load_agent_output, ValidationError


def test_valid_output(tmp_path: Path) -> None:
    valid_data = {
        "agent": "melchior",
        "verdict": "approve",
        "confidence": 0.95,
        "summary": "OK",
        "reasoning": "Reason",
        "findings": [],
        "recommendation": "Rec",
    }
    f = tmp_path / "valid.json"
    with open(f, "w") as j:
        json.dump(valid_data, j)

    loaded = load_agent_output(str(f))
    assert loaded["agent"] == "melchior"


def test_filters_extra_keys(tmp_path: Path) -> None:
    data = {
        "agent": "melchior",
        "verdict": "approve",
        "confidence": 0.95,
        "summary": "OK",
        "reasoning": "Reason",
        "findings": [],
        "recommendation": "Rec",
        "extra": "ignore me",
    }
    f = tmp_path / "extra.json"
    with open(f, "w") as j:
        json.dump(data, j)

    loaded = load_agent_output(str(f))
    assert "extra" not in loaded


def test_missing_keys(tmp_path: Path) -> None:
    data = {"agent": "melchior"}
    f = tmp_path / "missing.json"
    with open(f, "w") as j:
        json.dump(data, j)

    with pytest.raises(ValidationError):
        load_agent_output(str(f))


def test_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.json"
    f.touch()
    with pytest.raises(ValidationError):
        load_agent_output(str(f))
