# Test cases for skills/magi/scripts/reporting.py

import pytest
from typing import Any, Dict, List
from pathlib import Path

from reporting import (
    AGENT_TITLES,
    _agent_label,
    _fit_content,
    format_banner,
    format_report,
)

# Mock constants for testing
_BANNER_WIDTH: int = 52
_BANNER_INNER: int = _BANNER_WIDTH - 2
_FINDING_MARKER_WIDTH: int = 5
_FINDING_SEVERITY_WIDTH: int = 14


class TestReportingLogic:
    """Tests for the reporting functions."""

    def test_agent_title_mapping(self) -> None:
        """Test mapping of agent names to titles."""
        assert AGENT_TITLES["melchior"] == ("Melchior", "Scientist")
        assert AGENT_TITLES["balthasar"] == ("Balthasar", "Pragmatist")
        assert AGENT_TITLES["caspar"] == ("Caspar", "Critic")

    def test_agent_label_formatting(self) -> None:
        """Test formatting of agent labels."""
        assert _agent_label("melchior") == "Melchior (Scientist):"
        assert _agent_label("balthasar") == "Balthasar (Pragmatist):"
        assert _agent_label("caspar") == "Caspar (Critic):"
        assert _agent_label("unknown") == "Unknown (Agent):" # Test fallback

    def test_fit_content_no_truncation(self) -> None:
        """Test _fit_content when content fits within width."""
        short_text = "Short text"
        fitted = _fit_content(short_text, width=20)
        assert fitted == short_text

    def test_fit_content_truncation(self) -> None:
        """Test _fit_content when content needs truncation."""
        long_text = "This is a very long string that needs to be truncated."
        fitted = _fit_content(long_text, width=20)
        assert fitted == "This is a very..." # Ellipsis should be added

    def test_fit_content_truncation_with_suffix(self) -> None:
        """Test _fit_content with truncation and preserving a suffix."""
        long_text = "Short text and a suffix."
        suffix = "suffix."
        fitted = _fit_content(long_text, width=20, preserve_suffix=suffix)
        assert fitted == "Short text and a..." # Ellipsis replaces part of the text, suffix is kept

    def test_fit_content_suffix_too_long(self) -> None:
        """Test _fit_content where suffix alone exceeds width."""
        long_text = "Some text"
        suffix = "VeryLongSuffix"
        fitted = _fit_content(long_text, width=10, preserve_suffix=suffix)
        # Expect ellipsis to be added, no suffix if suffix itself is too long
        assert fitted == "Some tex..."

    def test_format_banner_basic(self) -> None:
        """Test basic banner formatting with 3 agents."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs tweak", "reasoning": "UI needs adjustment", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Critical issue", "recommendation": "Reject"},
        ]
        consensus = {"consensus": "HOLD (1-2)", "score": -0.33, "confidence": 0.60, "votes": {}, "dissent": [], "findings": [], "conditions": [], "recommendations": {}}
        banner = format_banner(agents, consensus)
        expected_lines = [
            "+" + "=" * (_BANNER_WIDTH - 2) + "+",
            "|          MAGI SYSTEM -- VERDICT          |",
            "+" + "=" * (_BANNER_WIDTH - 2) + "+",
            "|  Melchior (Scientist):          APPROVE (90%)   |",
            "|  Balthasar (Pragmatist):    CONDITIONAL (70%)  |",
            "|  Caspar (Critic):               REJECT (60%)   |",
            "+" + "=" * (_BANNER_WIDTH - 2) + "+",
            "|                  CONSENSUS: HOLD (1-2)                 |",
            "+" + "=" * (_BANNER_WIDTH - 2) + "+",
        ]
        assert banner.splitlines() == expected_lines

    def test_format_banner_truncation(self) -> None:
        """Test banner formatting with truncated agent names/verdicts."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "a_very_long_agent_name_indeed", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs tweak", "reasoning": "UI needs adjustment", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Critical issue", "recommendation": "Reject"},
        ]
        consensus = {"consensus": "HOLD (1-2)", "score": -0.33, "confidence": 0.60, "votes": {}, "dissent": [], "findings": [], "conditions": [], "recommendations": {}}
        banner = format_banner(agents, consensus)
        # Check that long agent name is truncated and the verdict suffix is preserved
        assert "|  A_very_long_agent_name_ind... CONDITIONAL (70%)  |" in banner

    def test_format_report_full(self) -> None:
        """Test formatting of a complete report."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [{"severity": "info", "title": "Info Finding 1", "detail": "Detail 1", "sources": ["melchior"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [{"severity": "warning", "title": "Warning Finding", "detail": "Detail 2", "sources": ["balthasar"]}], "summary": "Needs tweak", "reasoning": "UI needs adjustment", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Critical issue", "recommendation": "Reject"},
        ]
        consensus = {
            "consensus": "HOLD (1-2)",
            "score": -0.33,
            "confidence": 0.60,
            "votes": {},
            "dissent": [
                {"agent": "caspar", "summary": "Fail", "reasoning": "Critical issue"}
            ],
            "findings": [
                {"severity": "warning", "title": "Warning Finding", "detail": "Detail 2", "sources": ["balthasar"]},
                {"severity": "info", "title": "Info Finding 1", "detail": "Detail 1", "sources": ["melchior"]},
            ],
            "conditions": [
                {"agent": "balthasar", "condition": "Needs tweak"}
            ],
            "recommendations": {
                "melchior": "Merge",
                "balthasar": "Tweak UI",
                "caspar": "Reject"
            }
        }
        report = format_report(agents, consensus)
        report_lines = report.splitlines()

        # Check for banner
        assert "+==================================================+" in report_lines
        assert "|          MAGI SYSTEM -- VERDICT          |" in report_lines
        assert "+==================================================+" in report_lines
        assert "|  Melchior (Scientist):          APPROVE (90%)   |" in report_lines
        assert "|  Balthasar (Pragmatist):    CONDITIONAL (70%)  |" in report_lines
        assert "|  Caspar (Critic):               REJECT (60%)   |" in report_lines
        assert "|                  CONSENSUS: HOLD (1-2)                 |" in report_lines
        assert "+==================================================+" in report_lines
        assert "" in report_lines # Empty line after banner

        # Check for Findings section
        assert "## Key Findings" in report_lines
        assert "[!!] **[WARNING]**  Warning Finding _(from balthasar)_" in report_lines
        assert "[i]  **[INFO]**     Info Finding 1 _(from melchior)_" in report_lines

        # Check for Dissenting Opinion section
        assert "## Dissenting Opinion" in report_lines
        assert "**Caspar** (Critic): Fail" in report_lines
        assert "Critical issue" in report_lines # Check reasoning is included

        # Check for Conditions section
        assert "## Conditions for Approval" in report_lines
        assert "- **Balthasar**: Needs tweak" in report_lines

        # Check for Recommended Actions section
        assert "## Recommended Actions" in report_lines
        assert "- **Melchior** (Scientist): Merge" in report_lines
        assert "- **Balthasar** (Pragmatist): Tweak UI" in report_lines
        assert "- **Caspar** (Critic): Reject" in report_lines

    def test_format_report_no_findings_dissent_conditions(self) -> None:
        """Test report formatting when no findings, dissent, or conditions exist."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus = {
            "consensus": "STRONG GO",
            "score": 1.0,
            "confidence": 0.85,
            "votes": {},
            "dissent": [],
            "findings": [],
            "conditions": [],
            "recommendations": {"melchior": "Merge", "balthasar": "Merge"}
        }
        report = format_report(agents, consensus)
        report_lines = report.splitlines()

        assert "## Key Findings" not in report_lines
        assert "## Dissenting Opinion" not in report_lines
        assert "## Conditions for Approval" not in report_lines
        assert "## Recommended Actions" in report_lines
        assert "- **Melchior** (Scientist): Merge" in report_lines
        assert "- **Balthasar** (Pragmatist): Merge" in report_lines

    def test_format_report_with_many_agents_and_findings(self) -> None:
        """Test report formatting with more agents and findings, checking content fitting."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [{"severity": "info", "title": "Info Finding 1", "detail": "Detail 1", "sources": ["melchior"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [{"severity": "warning", "title": "Warning Finding", "detail": "Detail 2", "sources": ["balthasar"]}], "summary": "Needs tweak", "reasoning": "UI needs adjustment", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [{"severity": "critical", "title": "Critical Bug", "detail": "Detail 3", "sources": ["caspar"]}], "summary": "Fail", "reasoning": "Critical issue", "recommendation": "Reject"},
            {"agent": "agent_very_long_name_for_testing_banner", "verdict": "approve", "confidence": 0.5, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"}
        ]
        consensus = {
            "consensus": "HOLD (2-2)",
            "score": 0.0,
            "confidence": 0.65,
            "votes": {},
            "dissent": [
                {"agent": "caspar", "summary": "Fail", "reasoning": "Critical issue"},
                {"agent": "agent_very_long_name_for_testing_banner", "summary": "OK", "reasoning": "Fine"}
            ],
            "findings": [
                {"severity": "critical", "title": "Critical Bug", "detail": "Detail 3", "sources": ["caspar"]},
                {"severity": "warning", "title": "Warning Finding", "detail": "Detail 2", "sources": ["balthasar"]},
                {"severity": "info", "title": "Info Finding 1", "detail": "Detail 1", "sources": ["melchior"]},
            ],
            "conditions": [
                {"agent": "balthasar", "condition": "Needs tweak"}
            ],
            "recommendations": {
                "melchior": "Merge",
                "balthasar": "Tweak UI",
                "caspar": "Reject",
                "agent_very_long_name_for_testing_banner": "Merge"
            }
        }
        report = format_report(agents, consensus)
        report_lines = report.splitlines()

        # Check banner truncation for the long agent name
        assert "|  Agent_very_long_name_for_t...     APPROVE (50%)   |" in report_lines

        # Check findings are ordered by severity
        assert "[!!!] **[CRITICAL]**  Critical Bug _(from caspar)_" in report_lines
        assert "[!!]  **[WARNING]**   Warning Finding _(from balthasar)_" in report_lines
        assert "[i]   **[INFO]**      Info Finding 1 _(from melchior)_" in report_lines

        # Check dissent includes the long agent name and its reasoning
        assert "**Agent_very_long_name_for_t...**: OK" in report_lines
        assert "Fine" in report_lines # Check reasoning from the long named agent is included

        # Check recommendations include the long agent name
        assert "- **Agent_very_long_name_for_t...**: Merge" in report_lines
