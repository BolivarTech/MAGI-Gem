import json
import os
import re
from typing import Any

class ValidationError(Exception):
    def __init__(self, message: str, filepath: str = "") -> None:
        self.filepath = filepath
        super().__init__(f"{filepath}: {message}" if filepath else message)

VALID_AGENTS: set[str] = {"melchior", "balthasar", "caspar"}
VALID_VERDICTS: set[str] = {"approve", "reject", "conditional"}
VALID_SEVERITIES: set[str] = {"critical", "warning", "info"}

_REQUIRED_KEYS = frozenset({"agent", "verdict", "confidence", "summary", "reasoning", "findings", "recommendation"})
_REQUIRED_FINDING_KEYS = frozenset({"severity", "title", "detail"})
MAX_INPUT_FILE_SIZE: int = 10 * 1024 * 1024
_MAX_FINDINGS_PER_AGENT: int = 100
_MAX_FIELD_LENGTH: int = 50_000
_MAX_TITLE_LENGTH: int = 500
_MAX_DETAIL_LENGTH: int = 10_000

_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff\u00ad]")
_CONTROL_WHITESPACE_RE = re.compile(r"[\t\n\v\f\r\x85]")

def clean_title(raw: str) -> str:
    stripped_invisibles = _ZERO_WIDTH_RE.sub("", raw)
    without_breaks = _CONTROL_WHITESPACE_RE.sub(" ", stripped_invisibles)
    return without_breaks.strip()

def load_agent_output(filepath: str) -> dict[str, Any]:
    try:
        file_size = os.path.getsize(filepath)
        if file_size > MAX_INPUT_FILE_SIZE:
            raise ValidationError(f"File too large.", filepath)
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc}", filepath) from exc
    except OSError as exc:
        raise ValidationError(f"Cannot read file: {exc}", filepath) from exc

    if not isinstance(data, dict):
        raise ValidationError(f"Top-level JSON must be an object.", filepath)

    missing = _REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValidationError(f"Agent output missing keys: {sorted(missing)}", filepath)

    agent = data["agent"]
    if agent not in VALID_AGENTS:
        raise ValidationError(f"Unknown agent '{agent}'.", filepath)

    verdict = data["verdict"]
    if verdict not in VALID_VERDICTS:
        raise ValidationError(f"Invalid verdict '{verdict}'.", filepath)

    confidence = data["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise ValidationError(f"Confidence must be a number.", filepath)
    if not (0.0 <= confidence <= 1.0):
        raise ValidationError(f"Confidence must be between 0.0 and 1.0.", filepath)

    for field in ("summary", "reasoning", "recommendation"):
        if not isinstance(data[field], str):
            raise ValidationError(f"Field '{field}' must be a string.", filepath)
        if len(data[field]) > _MAX_FIELD_LENGTH:
            raise ValidationError(f"Field '{field}' too long.", filepath)

    findings = data["findings"]
    if not isinstance(findings, list):
        raise ValidationError(f"Findings must be a list.", filepath)
    for idx, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValidationError(f"Finding {idx} must be a dict.", filepath)
        f_missing = _REQUIRED_FINDING_KEYS - set(finding.keys())
        if f_missing:
            raise ValidationError(f"Finding {idx} missing keys.", filepath)
        if finding["severity"] not in VALID_SEVERITIES:
            raise ValidationError(f"Finding {idx} invalid severity.", filepath)
        cleaned = clean_title(finding["title"])
        if not cleaned:
            raise ValidationError(f"Finding {idx} empty title.", filepath)
        finding["title"] = cleaned

    return dict(data)
