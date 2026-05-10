import pytest
from consensus import determine_consensus

def test_consensus_unanimous_approve():
    agents = [
        {"agent": "melchior", "verdict": "approve", "confidence": 1.0, "summary": "S1", "reasoning": "R1", "findings": [], "recommendation": "Rec1"},
        {"agent": "balthasar", "verdict": "approve", "confidence": 1.0, "summary": "S2", "reasoning": "R2", "findings": [], "recommendation": "Rec2"},
        {"agent": "caspar", "verdict": "approve", "confidence": 1.0, "summary": "S3", "reasoning": "R3", "findings": [], "recommendation": "Rec3"},
    ]
    result = determine_consensus(agents)
    assert result["consensus_verdict"] == "approve"
    assert "STRONG GO" in result["consensus"]

def test_consensus_majority_reject():
    agents = [
        {"agent": "melchior", "verdict": "reject", "confidence": 1.0, "summary": "S1", "reasoning": "R1", "findings": [], "recommendation": "Rec1"},
        {"agent": "balthasar", "verdict": "approve", "confidence": 1.0, "summary": "S2", "reasoning": "R2", "findings": [], "recommendation": "Rec2"},
        {"agent": "caspar", "verdict": "reject", "confidence": 1.0, "summary": "S3", "reasoning": "R3", "findings": [], "recommendation": "Rec3"},
    ]
    result = determine_consensus(agents)
    assert result["consensus_verdict"] == "reject"
    assert "HOLD" in result["consensus"]
