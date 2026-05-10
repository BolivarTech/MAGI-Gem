# Test cases for skills/magi/scripts/consensus.py

import pytest
from typing import Any, Dict, List
from pathlib import Path

from consensus import (
    determine_consensus,
    VERDICT_WEIGHT,
    _deduplicate_findings,
    _severity_rank,
    _consensus_label,
    _agent_title,
)

# Mock constants for testing
_EPSILON: float = 1e-9


class TestConsensusLogic:
    """Tests for the consensus determination logic."""

    def test_strong_go_consensus(self) -> None:
        """All agents approve."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "caspar", "verdict": "approve", "confidence": 0.7, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "STRONG GO"
        assert consensus["score"] == pytest.approx(1.0)
        assert consensus["confidence"] == pytest.approx(0.8)  # Avg confidence of majority (all)

    def test_strong_no_go_consensus(self) -> None:
        """All agents reject."""
        agents = [
            {"agent": "melchior", "verdict": "reject", "confidence": 0.9, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
            {"agent": "balthasar", "verdict": "reject", "confidence": 0.8, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.7, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "STRONG NO-GO"
        assert consensus["score"] == pytest.approx(-1.0)
        assert consensus["confidence"] == pytest.approx(0.8) # Avg confidence of majority (all)

    def test_go_with_caveats(self) -> None:
        """Two approve, one conditional."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "caspar", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs minor change", "reasoning": "One small fix", "recommendation": "Fix and resubmit"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "GO WITH CAVEATS (2-1)"
        assert consensus["score"] == pytest.approx((1.0 + 1.0 + 0.5) / 3)
        assert consensus["confidence"] == pytest.approx(0.85) # Avg confidence of majority (2 approvers)

    def test_hold_with_split_votes(self) -> None:
        """One approve, one conditional, one reject."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs fix", "reasoning": "One small fix", "recommendation": "Fix and resubmit"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "HOLD (1-2)"
        assert consensus["score"] == pytest.approx((1.0 + 0.5 - 1.0) / 3)
        assert consensus["confidence"] == pytest.approx(0.6) # Avg confidence of majority (reject+conditional)

    def test_hold_with_tie(self) -> None:
        """One approve, one reject."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "reject", "confidence": 0.8, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "HOLD (1-1)"
        assert consensus["score"] == pytest.approx(0.0)
        assert consensus["confidence"] == pytest.approx(0.85) # Avg confidence of majority (tie, but formula uses sum(majorities)/num_agents)

    def test_findings_deduplication_and_severity(self) -> None:
        """Test that findings are deduplicated and severity is the minimum."""
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [
                    {"severity": "critical", "title": "Critical Bug", "detail": "Detail A", "sources": ["melchior"]},
                    {"severity": "info", "title": "Info Finding", "detail": "Detail B", "sources": ["melchior"]},
                ],
                "summary": "OK", "reasoning": "Fine", "recommendation": "Merge",
            },
            {
                "agent": "balthasar",
                "verdict": "approve",
                "confidence": 0.8,
                "findings": [
                    {"severity": "warning", "title": "Critical Bug", "detail": "Detail C (from Balthasar)", "sources": ["balthasar"]},
                    {"severity": "info", "title": "Another Info", "detail": "Detail D", "sources": ["balthasar"]},
                ],
                "summary": "OK", "reasoning": "Fine", "recommendation": "Merge",
            },
            {
                "agent": "caspar",
                "verdict": "approve",
                "confidence": 0.7,
                "findings": [
                    {"severity": "critical", "title": "Critical Bug", "detail": "Detail E (from Caspar)", "sources": ["caspar"]},
                    {"severity": "warning", "title": "Another Warning", "detail": "Detail F", "sources": ["caspar"]},
                ],
                "summary": "OK", "reasoning": "Fine", "recommendation": "Merge",
            },
        ]
        consensus = determine_consensus(agents)
        deduped_findings = consensus["findings"]

        assert len(deduped_findings) == 4 # Critical Bug, Info Finding, Another Info, Another Warning

        # Check Critical Bug: lowest severity is critical, detail/sources from first agent that had critical
        critical_bug = next(f for f in deduped_findings if f["title"] == "Critical Bug")
        assert critical_bug["severity"] == "critical"
        assert critical_bug["detail"] == "Detail A" # Detail from Melchior (first critical)
        assert sorted(critical_bug["sources"]) == ["balthasar", "caspar", "melchior"]

        # Check Info Finding
        info_finding = next(f for f in deduped_findings if f["title"] == "Info Finding")
        assert info_finding["severity"] == "info"
        assert info_finding["detail"] == "Detail B"
        assert info_finding["sources"] == ["melchior"]

        # Check Another Info
        another_info = next(f for f in deduped_findings if f["title"] == "Another Info")
        assert another_info["severity"] == "info"
        assert another_info["detail"] == "Detail D"
        assert another_info["sources"] == ["balthasar"]

        # Check Another Warning
        another_warning = next(f for f in deduped_findings if f["title"] == "Another Warning")
        assert another_warning["severity"] == "warning"
        assert another_warning["detail"] == "Detail F"
        assert another_warning["sources"] == ["caspar"]

    def test_deduplicate_key_cleaning(self) -> None:
        """Ensure title cleaning works for deduplication key."""
        # Test cleaning of invisible chars and whitespace for deduplication
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [{"severity": "info", "title": "  \u200bTitle with	Spaces ", "detail": "Detail 1", "sources": ["melchior"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [{"severity": "warning", "title": "Title with Spaces", "detail": "Detail 2", "sources": ["balthasar"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus = determine_consensus(agents)
        assert len(consensus["findings"]) == 1
        assert consensus["findings"][0]["title"] == "Title with Spaces" # Cleaned title
        assert consensus["findings"][0]["sources"] == ["balthasar", "melchior"] # Both agents contributed

    def test_conditions_aggregation(self) -> None:
        """Test aggregation of conditions from conditional verdicts."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs UI tweak", "reasoning": "UI could be better", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "conditional", "confidence": 0.6, "findings": [], "summary": "Needs performance optimization", "reasoning": "Slows down on large data", "recommendation": "Optimize performance"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "GO WITH CAVEATS (2-1)"
        assert len(consensus["conditions"]) == 2
        # Check that conditions are correctly associated with agents
        cond_agents = {c["agent"] for c in consensus["conditions"]}
        assert cond_agents == {"balthasar", "caspar"}
        assert any(c["condition"] == "Needs UI tweak" for c in consensus["conditions"])
        assert any(c["condition"] == "Needs performance optimization" for c in consensus["conditions"])

    def test_dissent_aggregation(self) -> None:
        """Test aggregation of dissent information."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "reject", "confidence": 0.7, "findings": [], "summary": "Critical flaw found", "reasoning": "Security vulnerability", "recommendation": "Reject immediately"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Unacceptable performance", "reasoning": "Too slow for production", "recommendation": "Reject"},
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "STRONG NO-GO"
        assert len(consensus["dissent"]) == 2
        # Check that dissent info is correctly aggregated
        dissent_agents = {d["agent"] for d in consensus["dissent"]}
        assert dissent_agents == {"balthasar", "caspar"}
        assert any(d["summary"] == "Critical flaw found" for d in consensus["dissent"])
        assert any(d["reasoning"] == "Security vulnerability" for d in consensus["dissent"])

    def test_recommendations_aggregation(self) -> None:
        """Test aggregation of recommendations."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "conditional", "confidence": 0.7, "findings": [], "summary": "Needs UI tweak", "reasoning": "UI could be better", "recommendation": "Tweak UI"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus = determine_consensus(agents)
        recs = consensus["recommendations"]
        assert recs["melchior"] == "Merge"
        assert recs["balthasar"] == "Tweak UI"
        assert recs["caspar"] == "Reject"

    def test_confidence_calculation(self) -> None:
        """Test the confidence calculation logic."""
        # Scenario 1: All approve with varying confidences
        agents1 = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "caspar", "verdict": "approve", "confidence": 0.7, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus1 = determine_consensus(agents1)
        # Score = 1.0. Confidence = (0.9+0.8+0.7)/3 * (abs(1.0)+1)/2 = 0.8 * 1.0 = 0.8
        assert consensus1["confidence"] == pytest.approx(0.80)

        # Scenario 2: Mixed votes, score > 0
        agents2 = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus2 = determine_consensus(agents2)
        # Majority agents: melchior, balthasar. Score = (1+1-1)/3 = 0.333...
        # Confidence = (0.9+0.8)/2 * (abs(0.333)+1)/2 = 0.85 * 0.666... = 0.5666...
        assert consensus2["confidence"] == pytest.approx(0.57) # Rounded to 2 decimals

        # Scenario 3: Mixed votes, score <= 0
        agents3 = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "reject", "confidence": 0.8, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
            {"agent": "caspar", "verdict": "reject", "confidence": 0.6, "findings": [], "summary": "Fail", "reasoning": "Bad", "recommendation": "Reject"},
        ]
        consensus3 = determine_consensus(agents3)
        # Majority agents: balthasar, caspar. Score = (1-1-1)/3 = -0.333...
        # Confidence = (0.8+0.6)/2 * (abs(-0.333)+1)/2 = 0.7 * 0.666... = 0.4666...
        assert consensus3["confidence"] == pytest.approx(0.47) # Rounded to 2 decimals

    def test_finding_sources_aggregation(self) -> None:
        """Test that sources are aggregated correctly when findings are deduplicated."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [{"severity": "info", "title": "Same Title", "detail": "Detail A", "sources": ["melchior"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [{"severity": "info", "title": "Same Title", "detail": "Detail B", "sources": ["balthasar"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus = determine_consensus(agents)
        deduped_finding = consensus["findings"][0]
        assert deduped_finding["title"] == "Same Title"
        assert sorted(deduped_finding["sources"]) == ["balthasar", "melchior"]

    def test_severity_rank_for_deduplication(self) -> None:
        """Ensure severity ranking is correctly used for deduplication."""
        agents = [
            {"agent": "melchior", "verdict": "approve", "confidence": 0.9, "findings": [{"severity": "critical", "title": "Test Finding", "detail": "Detail Critical", "sources": ["melchior"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "balthasar", "verdict": "approve", "confidence": 0.8, "findings": [{"severity": "warning", "title": "Test Finding", "detail": "Detail Warning", "sources": ["balthasar"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
            {"agent": "caspar", "verdict": "approve", "confidence": 0.7, "findings": [{"severity": "info", "title": "Test Finding", "detail": "Detail Info", "sources": ["caspar"]}], "summary": "OK", "reasoning": "Fine", "recommendation": "Merge"},
        ]
        consensus = determine_consensus(agents)
        deduped_finding = consensus["findings"][0]
        assert deduped_finding["title"] == "Test Finding"
        assert deduped_finding["severity"] == "critical" # Critical should be chosen
        assert deduped_finding["detail"] == "Detail Critical" # Detail from critical source
        assert sorted(deduped_finding["sources"]) == ["balthasar", "caspar", "melchior"]

    def test_agent_title_helper(self) -> None:
        """Test the internal agent title helper function."""
        assert _agent_title("melchior") == ("Melchior", "Scientist")
        assert _agent_title("balthasar") == ("Balthasar", "Pragmatist")
        assert _agent_title("caspar") == ("Caspar", "Critic")
        assert _agent_title("unknown_agent") == ("Unknown_agent", "Agent") # Test fallback
