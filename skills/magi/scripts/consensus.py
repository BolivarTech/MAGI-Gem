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

def _consensus_short_verdict(score: float, has_conditions: bool) -> str:
    if abs(score - 1.0) < _EPSILON: return "approve"
    if abs(score - (-1.0)) < _EPSILON: return "reject"
    is_positive = score > _EPSILON
    if is_positive and has_conditions: return "conditional"
    if is_positive: return "approve"
    return "reject"

def _format_consensus_label(score: float, consensus_short: str, split: tuple[int, int]) -> str:
    if abs(score - 1.0) < _EPSILON: return "STRONG GO"
    if abs(score - (-1.0)) < _EPSILON: return "STRONG NO-GO"
    if abs(score) < _EPSILON: return "HOLD -- TIE"
    split_label = f"({split[0]}-{split[1]})"
    if consensus_short == "conditional": return f"GO WITH CAVEATS {split_label}"
    if consensus_short == "approve": return f"GO {split_label}"
    return f"HOLD {split_label}"

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
    return sorted(findings_by_title.values(), key=lambda f: _severity_rank(f["severity"]))

def _compute_confidence(majority_agents: list[dict[str, Any]], num_agents: int, score: float) -> float:
    majority_conf: float = sum(a["confidence"] for a in majority_agents)
    base_confidence = majority_conf / num_agents
    weight_factor = (abs(score) + 1) / 2
    return float(round(max(0.0, min(1.0, base_confidence * weight_factor)), 2))

def determine_consensus(agents: list[dict[str, Any]]) -> dict[str, Any]:
    num_agents = len(agents)
    verdicts = [a["verdict"] for a in agents]
    score = sum(VERDICT_WEIGHT[v] for v in verdicts) / num_agents
    has_conditions = "conditional" in verdicts
    consensus_short = _consensus_short_verdict(score, has_conditions)
    consensus_side = "reject" if consensus_short == "reject" else "approve"
    majority_agents = []
    dissent_agents = []
    for a in agents:
        eff = "approve" if a["verdict"] == "conditional" else a["verdict"]
        if eff == consensus_side: majority_agents.append(a)
        else: dissent_agents.append(a)
    split = (len(majority_agents), len(dissent_agents))
    consensus = _format_consensus_label(score, consensus_short, split)
    all_findings = _deduplicate_findings(agents)
    conditions = [{"agent": a["agent"], "condition": a["summary"]} for a in agents if a["verdict"] == "conditional"]
    confidence = _compute_confidence(majority_agents, num_agents, score)
    return {
        "consensus": consensus,
        "consensus_verdict": consensus_short,
        "confidence": confidence,
        "votes": {a["agent"]: a["verdict"] for a in agents},
        "majority_summary": " | ".join(f"{a['agent'].capitalize()}: {a['summary']}" for a in majority_agents),
        "dissent": [{"agent": a["agent"], "summary": a["summary"], "reasoning": a["reasoning"]} for a in dissent_agents],
        "findings": all_findings,
        "conditions": conditions,
        "recommendations": {a["agent"]: a["recommendation"] for a in agents},
    }
