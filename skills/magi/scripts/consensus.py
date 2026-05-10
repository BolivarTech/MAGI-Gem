from __future__ import annotations
import unicodedata
from typing import Any
from validate import clean_title

VERDICT_WEIGHT: dict[str, float] = {
    "approve": 1,
    "conditional": 0.5,
    "reject": -1,
}

_SEVERITY_ORDER: dict[str, int] = {"critical": 0, "warning": 1, "info": 2}
_UNKNOWN_SEVERITY_RANK = 99
_EPSILON: float = 1e-9


def _severity_rank(severity: str) -> int:
    return _SEVERITY_ORDER.get(severity, _UNKNOWN_SEVERITY_RANK)


def _dedup_key(title: str) -> str:
    return unicodedata.normalize("NFKC", clean_title(title)).casefold()


def _deduplicate_findings(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings_by_title: dict[str, dict[str, Any]] = {}
    for a in agents:
        for f in a.get("findings", []):
            title_key = _dedup_key(f["title"])
            existing = findings_by_title.get(title_key)
            if existing is None:
                findings_by_title[title_key] = {**f, "sources": [a["agent"]]}
                continue
            existing["sources"].append(a["agent"])
            if _severity_rank(f["severity"]) < _severity_rank(existing["severity"]):
                existing["severity"] = f["severity"]
                existing["detail"] = f["detail"]
    return sorted(
        findings_by_title.values(), key=lambda f: _severity_rank(f["severity"])
    )


def _consensus_label(score: float, has_conditions: bool, split: tuple[int, int]) -> str:
    if abs(score - 1.0) < _EPSILON:
        return "STRONG GO"
    if abs(score - (-1.0)) < _EPSILON:
        return "STRONG NO-GO"

    split_label = f"({split[0]}-{split[1]})"
    if score > _EPSILON:
        if has_conditions:
            return f"GO WITH CAVEATS {split_label}"
        return f"GO {split_label}"

    return f"HOLD {split_label}"


def determine_consensus(agents: list[dict[str, Any]]) -> dict[str, Any]:
    num_agents = len(agents)
    verdicts = [a["verdict"] for a in agents]
    score = sum(VERDICT_WEIGHT[v] for v in verdicts) / num_agents
    has_conditions = "conditional" in verdicts

    # Majority logic:
    # For score > 0, majority are those who didn't 'reject'
    # For score <= 0, majority are those who 'reject' (or it's a tie)
    if score > _EPSILON:
        majority_agents = [
            a for a in agents if a["verdict"] in ("approve", "conditional")
        ]
        dissent_agents = [a for a in agents if a["verdict"] == "reject"]
    else:
        majority_agents = [a for a in agents if a["verdict"] == "reject"]
        dissent_agents = [
            a for a in agents if a["verdict"] in ("approve", "conditional")
        ]

    split = (len(majority_agents), len(dissent_agents))
    consensus_text = _consensus_label(score, has_conditions, split)

    all_findings = _deduplicate_findings(agents)
    conditions = [
        {"agent": a["agent"], "condition": a["summary"]}
        for a in agents
        if a["verdict"] == "conditional"
    ]

    # New Confidence Formula:
    # weight_factor = (abs(score) + 1) / 2
    # base_confidence = sum(majority_confidence) / num_agents
    # confidence = base_confidence * weight_factor
    weight_factor = (abs(score) + 1) / 2
    base_confidence = sum(a["confidence"] for a in majority_agents) / num_agents
    confidence = float(round(base_confidence * weight_factor, 2))

    return {
        "consensus": consensus_text,
        "score": score,
        "confidence": confidence,
        "votes": {a["agent"]: a["verdict"] for a in agents},
        "dissent": [
            {"agent": a["agent"], "summary": a["summary"], "reasoning": a["reasoning"]}
            for a in dissent_agents
        ],
        "findings": all_findings,
        "conditions": conditions,
        "recommendations": {a["agent"]: a["recommendation"] for a in agents},
    }
