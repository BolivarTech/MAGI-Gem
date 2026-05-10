# Test cases for skills/magi/scripts/consensus.py

import pytest
from consensus import (
    determine_consensus,
)

_EPSILON: float = 1e-9


class TestConsensusLogic:
    """Tests for the consensus determination logic."""

    def test_strong_go_consensus(self) -> None:
        """All agents approve."""
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "approve",
                "confidence": 0.8,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "caspar",
                "verdict": "approve",
                "confidence": 0.7,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "STRONG GO"
        assert consensus["score"] == pytest.approx(1.0)
        assert consensus["confidence"] == pytest.approx(0.8)

    def test_strong_no_go_consensus(self) -> None:
        """All agents reject."""
        agents = [
            {
                "agent": "melchior",
                "verdict": "reject",
                "confidence": 0.9,
                "findings": [],
                "summary": "Fail",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "reject",
                "confidence": 0.8,
                "findings": [],
                "summary": "Fail",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "caspar",
                "verdict": "reject",
                "confidence": 0.7,
                "findings": [],
                "summary": "Fail",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        assert consensus["consensus"] == "STRONG NO-GO"
        assert consensus["score"] == pytest.approx(-1.0)
        assert consensus["confidence"] == pytest.approx(0.8)

    def test_go_with_caveats(self) -> None:
        """Two approve, one conditional."""
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "approve",
                "confidence": 0.8,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "caspar",
                "verdict": "conditional",
                "confidence": 0.7,
                "findings": [],
                "summary": "Cond",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        # Score = (1 + 1 + 0.5) / 3 = 0.833...
        # majority_agents = all 3 (approve + conditional are > 0)
        # split = (3, 0)
        assert consensus["consensus"] == "GO WITH CAVEATS (3-0)"
        assert consensus["score"] == pytest.approx(0.833333333)
        # base_confidence = (0.9 + 0.8 + 0.7) / 3 = 0.8
        # weight_factor = (0.833... + 1) / 2 = 0.9166...
        # confidence = 0.8 * 0.9166... = 0.7333... -> 0.73
        assert consensus["confidence"] == pytest.approx(0.73)

    def test_hold_with_split_votes(self) -> None:
        """One approve, one conditional, one reject."""
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [],
                "summary": "OK",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "conditional",
                "confidence": 0.7,
                "findings": [],
                "summary": "Cond",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "caspar",
                "verdict": "reject",
                "confidence": 0.6,
                "findings": [],
                "summary": "Fail",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        # Score = (1 + 0.5 - 1) / 3 = 0.166...
        # majority_agents = [melchior, balthasar] (2). dissent_agents = [caspar] (1).
        # split = (2, 1)
        assert consensus["consensus"] == "GO WITH CAVEATS (2-1)"
        assert consensus["score"] == pytest.approx(0.166666666)

    def test_findings_deduplication(self) -> None:
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [
                    {"severity": "critical", "title": "Bug", "detail": "Det A"},
                ],
                "summary": "S",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "approve",
                "confidence": 0.8,
                "findings": [
                    {"severity": "warning", "title": "Bug", "detail": "Det B"},
                ],
                "summary": "S",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        assert len(consensus["findings"]) == 1
        assert consensus["findings"][0]["severity"] == "critical"
        assert sorted(consensus["findings"][0]["sources"]) == ["balthasar", "melchior"]

    def test_confidence_calculation_logic(self) -> None:
        # 2 approve, 1 reject
        agents = [
            {
                "agent": "melchior",
                "verdict": "approve",
                "confidence": 0.9,
                "findings": [],
                "summary": "S",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "balthasar",
                "verdict": "approve",
                "confidence": 0.8,
                "findings": [],
                "summary": "S",
                "reasoning": "R",
                "recommendation": "Rec",
            },
            {
                "agent": "caspar",
                "verdict": "reject",
                "confidence": 0.6,
                "findings": [],
                "summary": "S",
                "reasoning": "R",
                "recommendation": "Rec",
            },
        ]
        consensus = determine_consensus(agents)
        # Score = (1 + 1 - 1) / 3 = 0.333...
        # Majority = [melchior, balthasar]. base_conf = (0.9 + 0.8) / 2 = 0.85
        # weight_factor = (0.333... + 1) / 2 = 0.666...
        # confidence = 0.85 * 0.666... = 0.5666... -> 0.57
        assert consensus["confidence"] == pytest.approx(0.57)
