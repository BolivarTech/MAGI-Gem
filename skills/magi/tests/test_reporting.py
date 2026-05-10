# Test cases for skills/magi/scripts/reporting.py

from reporting import (
    _fit_content,
    format_banner,
    format_report,
)


def test_fit_content_basic() -> None:
    assert _fit_content("short", 10) == "short"
    assert _fit_content("very long string", 10) == "very lo..."


def test_fit_content_with_suffix() -> None:
    # width 20, suffix 7 ("suffix."), ellipsis 3. budget = 20 - 3 - 7 = 10.
    # prefix "Short text and a " (17). fits 10? no -> "Short text..."
    # result "Short text...suffix."
    fitted = _fit_content("Short text and a suffix.", 20, preserve_suffix="suffix.")
    assert fitted == "Short text...suffix."


def test_format_banner_width() -> None:
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
    ]
    consensus = {"consensus": "STRONG GO"}
    banner = format_banner(agents, consensus)
    lines = banner.splitlines()
    for line in lines:
        assert len(line) == 52  # Standard width in implementation


def test_format_report_smoke() -> None:
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
    ]
    consensus = {
        "consensus": "STRONG GO",
        "findings": [],
        "dissent": [],
        "conditions": [],
        "recommendations": {"melchior": "Rec"},
    }
    report = format_report(agents, consensus)
    assert "MAGI SYSTEM -- VERDICT" in report
    assert "STRONG GO" in report
