# Test cases for skills/magi/scripts/validate.py

import json
import os
import re
from typing import Any
from pathlib import Path

import pytest

from validate import (
    ValidationError,
    VALID_AGENTS,
    VALID_SEVERITIES,
    VALID_VERDICTS,
    clean_title,
    load_agent_output,
)

# Mock constants from validate.py to control test behavior if needed
# MAX_INPUT_FILE_SIZE = 10 * 1024 * 1024
# _MAX_FINDINGS_PER_AGENT: int = 100
# _MAX_FIELD_LENGTH: int = 50_000
# _MAX_TITLE_LENGTH: int = 500
# _MAX_DETAIL_LENGTH: int = 10_000


class TestValidateAgentOutput:
    """Tests for the load_agent_output function in validate.py."""

    def test_valid_output(self, tmp_path: Path) -> None:
        """Test with a perfectly valid agent output."""
        valid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.95,
            "summary": "All systems nominal.",
            "reasoning": "The analysis confirms expected behavior.",
            "findings": [
                {
                    "severity": "info",
                    "title": "Code style adheres to project conventions.",
                    "detail": "Minor formatting adjustments were applied.",
                    "sources": ["melchior"],
                }
            ],
            "recommendation": "Proceed with deployment.",
        }
        output_file = tmp_path / "valid_agent_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        loaded_data = load_agent_output(str(output_file))
        assert loaded_data == valid_data
        # Check title cleaning
        assert loaded_data["findings"][0]["title"] == "Code style adheres to project conventions."

    def test_output_with_extra_keys(self, tmp_path: Path) -> None:
        """Test that extra keys are ignored."""
        data_with_extra = {
            "agent": "balthasar",
            "verdict": "conditional",
            "confidence": 0.7,
            "summary": "Functionality is good, but needs minor refactoring.",
            "reasoning": "The core logic works, but code could be cleaner.",
            "findings": [],
            "recommendation": "Refactor before merging.",
            "extra_field": "this should be ignored",
        }
        output_file = tmp_path / "extra_keys_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data_with_extra, f)

        loaded_data = load_agent_output(str(output_file))
        assert "extra_field" not in loaded_data
        assert loaded_data["agent"] == "balthasar"

    def test_missing_required_keys(self, tmp_path: Path) -> None:
        """Test that missing required keys raise ValidationError."""
        invalid_data = {
            "agent": "caspar",
            "confidence": 0.6,
            "summary": "Potential issues identified.",
        }  # Missing verdict, reasoning, findings, recommendation
        output_file = tmp_path / "missing_keys_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Agent output missing keys: .*verdict.*"):
            load_agent_output(str(output_file))

    def test_invalid_agent_name(self, tmp_path: Path) -> None:
        """Test with an unknown agent name."""
        invalid_data = {
            "agent": "unknown_agent",
            "verdict": "approve",
            "confidence": 1.0,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "invalid_agent_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Unknown agent 'unknown_agent'"):
            load_agent_output(str(output_file))

    def test_invalid_verdict(self, tmp_path: Path) -> None:
        """Test with an invalid verdict."""
        invalid_data = {
            "agent": "melchior",
            "verdict": "maybe",
            "confidence": 0.5,
            "summary": "Unsure",
            "reasoning": "Needs more context",
            "findings": [],
            "recommendation": "Hold for review",
        }
        output_file = tmp_path / "invalid_verdict_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Invalid verdict 'maybe'"):
            load_agent_output(str(output_file))

    def test_invalid_confidence_type(self, tmp_path: Path) -> None:
        """Test confidence field with incorrect type."""
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": "high",
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "invalid_confidence_type.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Confidence must be a number"):
            load_agent_output(str(output_file))

    def test_confidence_out_of_range(self, tmp_path: Path) -> None:
        """Test confidence field out of 0.0-1.0 range."""
        invalid_data_low = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": -0.1,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [],
            "recommendation": "Merge",
        }
        invalid_data_high = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 1.1,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [],
            "recommendation": "Merge",
        }
        output_file_low = tmp_path / "confidence_low.json"
        output_file_high = tmp_path / "confidence_high.json"

        with open(output_file_low, "w", encoding="utf-8") as f:
            json.dump(invalid_data_low, f)
        with open(output_file_high, "w", encoding="utf-8") as f:
            json.dump(invalid_data_high, f)

        with pytest.raises(ValidationError, match="Confidence must be between 0.0 and 1.0"):
            load_agent_output(str(output_file_low))
        with pytest.raises(ValidationError, match="Confidence must be between 0.0 and 1.0"):
            load_agent_output(str(output_file_high))

    def test_invalid_findings_type(self, tmp_path: Path) -> None:
        """Test 'findings' field with incorrect type."""
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": "This should be a list",
            "recommendation": "Merge",
        }
        output_file = tmp_path / "invalid_findings_type.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Findings must be a list"):
            load_agent_output(str(output_file))

    def test_finding_missing_keys(self, tmp_path: Path) -> None:
        """Test a finding with missing keys."""
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [
                {"severity": "warning", "title": "Missing detail field"}
            ],  # Missing detail
            "recommendation": "Merge",
        }
        output_file = tmp_path / "finding_missing_keys.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Finding 0 missing keys"):
            load_agent_output(str(output_file))

    def test_finding_invalid_severity(self, tmp_path: Path) -> None:
        """Test a finding with an invalid severity."""
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [
                {
                    "severity": "extreme",
                    "title": "This severity is not valid.",
                    "detail": "Severity must be critical, warning, or info.",
                }
            ],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "finding_invalid_severity.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Finding 0 invalid severity"):
            load_agent_output(str(output_file))

    def test_finding_title_cleaning(self, tmp_path: Path) -> None:
        """Test that finding titles are cleaned."""
        data = {
            "agent": "balthasar",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [
                {
                    "severity": "info",
                    "title": "\u200bZero Width Space	Tab
Newline",  # Mixed invisible chars & whitespace
                    "detail": "This detail should be preserved.",
                }
            ],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "finding_title_cleaning.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded_data = load_agent_output(str(output_file))
        # Expected: invisible chars removed, whitespace replaced by single space
        assert loaded_data["findings"][0]["title"] == "Zero Width Space Tab Newline"

    def test_field_length_exceeded(self, tmp_path: Path) -> None:
        """Test that fields exceeding max length raise an error."""
        long_string = "a" * 60000  # Exceeds _MAX_FIELD_LENGTH (50_000)
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": long_string,  # Exceeds length
            "findings": [],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "field_length_exceeded.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Field 'reasoning' too long"):
            load_agent_output(str(output_file))

    def test_title_length_exceeded(self, tmp_path: Path) -> None:
        """Test that finding titles exceeding max length raise an error."""
        long_title = "b" * 600  # Exceeds _MAX_TITLE_LENGTH (500)
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [
                {
                    "severity": "info",
                    "title": long_title,
                    "detail": "This is a detail.",
                }
            ],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "title_length_exceeded.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        # Note: clean_title might truncate, so we check for the error raised *after* cleaning
        # If clean_title truncates and the resulting string is still too long, it might error out later
        # For now, let's assume clean_title happens first and the error is raised.
        # The validate.py logic cleans title *before* checking length, so we expect error here.
        with pytest.raises(ValidationError, match="Finding 0 title.*"):
            load_agent_output(str(output_file))

    def test_detail_length_exceeded(self, tmp_path: Path) -> None:
        """Test that finding details exceeding max length raise an error."""
        long_detail = "c" * 12000  # Exceeds _MAX_DETAIL_LENGTH (10_000)
        invalid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "OK",
            "reasoning": "Fine",
            "findings": [
                {
                    "severity": "info",
                    "title": "Valid Title",
                    "detail": long_detail,
                }
            ],
            "recommendation": "Merge",
        }
        output_file = tmp_path / "detail_length_exceeded.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Finding 0 detail too long"):
            load_agent_output(str(output_file))

    def test_empty_json_file(self, tmp_path: Path) -> None:
        """Test loading an empty JSON file."""
        output_file = tmp_path / "empty.json"
        output_file.touch()  # Create an empty file

        with pytest.raises(ValidationError, match="Invalid JSON: .*empty file"):
            load_agent_output(str(output_file))

    def test_non_json_file(self, tmp_path: Path) -> None:
        """Test loading a file that is not JSON."""
        output_file = tmp_path / "not_json.json"
        output_file.write_text("This is not JSON.")

        with pytest.raises(ValidationError, match="Invalid JSON: .*Not JSON"):
            load_agent_output(str(output_file))

    def test_file_too_large(self, tmp_path: Path) -> None:
        """Test that files exceeding MAX_INPUT_FILE_SIZE raise an error."""
        # Create a file larger than MAX_INPUT_FILE_SIZE
        large_content = "a" * (10 * 1024 * 1024 + 1)
        output_file = tmp_path / "too_large.json"
        output_file.write_text(large_content)

        with pytest.raises(ValidationError, match="File too large"):
            load_agent_output(str(output_file))

    def test_finding_with_sources_field(self, tmp_path: Path) -> None:
        """Test a finding object that includes the 'sources' field."""
        valid_data = {
            "agent": "melchior",
            "verdict": "approve",
            "confidence": 0.95,
            "summary": "All systems nominal.",
            "reasoning": "The analysis confirms expected behavior.",
            "findings": [
                {
                    "severity": "info",
                    "title": "Code style adheres to project conventions.",
                    "detail": "Minor formatting adjustments were applied.",
                    "sources": ["melchior", "balthasar"], # Test with multiple sources
                }
            ],
            "recommendation": "Proceed with deployment.",
        }
        output_file = tmp_path / "finding_with_sources.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        loaded_data = load_agent_output(str(output_file))
        assert loaded_data["findings"][0]["sources"] == ["melchior", "balthasar"]

    def test_findings_list_is_empty(self, tmp_path: Path) -> None:
        """Test agent output where the findings list is empty."""
        valid_data = {
            "agent": "balthasar",
            "verdict": "approve",
            "confidence": 0.9,
            "summary": "No issues found.",
            "reasoning": "The code is clean and well-structured.",
            "findings": [], # Empty findings list
            "recommendation": "Approve as is.",
        }
        output_file = tmp_path / "empty_findings.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        loaded_data = load_agent_output(str(output_file))
        assert loaded_data["findings"] == []

    def test_top_level_is_not_object(self, tmp_path: Path) -> None:
        """Test that a JSON array at the top level is rejected."""
        invalid_data = [
            {"agent": "melchior", "verdict": "approve", "confidence": 1.0, "summary": "OK", "reasoning": "Fine", "findings": [], "recommendation": "Merge"}
        ]
        output_file = tmp_path / "not_object.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValidationError, match="Top-level JSON must be an object"):
            load_agent_output(str(output_file))
