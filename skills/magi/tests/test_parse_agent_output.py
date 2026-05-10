import json
import pytest
from pathlib import Path
from parse_agent_output import parse_agent_output


def test_parse_gemini_wrapped_json(tmp_path: Path) -> None:
    """Test parsing the new Gemini CLI output format."""
    raw_json = {
        "response": """```json
{"agent": "melchior", "verdict": "approve", "confidence": 1.0, "summary": "OK", "reasoning": "...", "findings": [], "recommendation": "..."}
```""",
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)
    assert data["agent"] == "melchior"
    assert data["verdict"] == "approve"


def test_parse_raw_unfenced_json(tmp_path: Path) -> None:
    """Test parsing if Gemini returns JSON without fences."""
    raw_json = {
        "response": '{"agent": "balthasar", "verdict": "reject", "confidence": 0.5, "summary": "No", "reasoning": "...", "findings": [], "recommendation": "..."}',
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)
    assert data["agent"] == "balthasar"
    assert data["verdict"] == "reject"


def test_parse_with_extra_whitespace(tmp_path: Path) -> None:
    """Test parsing JSON with extraneous whitespace within and around."""
    raw_json = {
        "response": """  ```json  
 { 
 "agent": "caspar" ,
 "verdict" : "approve"
 }
 ```  """,
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)
    assert data["agent"] == "caspar"
    assert data["verdict"] == "approve"


def test_parse_with_control_characters(tmp_path: Path) -> None:
    """Test parsing JSON that includes control characters (like tabs, newlines)."""
    raw_json = {
        "response": """```json
{"agent": "melchior", "verdict": "approve", "summary": "OK\\nwith\\ttabs", "reasoning": "...", "findings": [], "recommendation": "..."}
```""",
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)
    assert data["summary"] == "OK\nwith\ttabs"


def test_parse_json_with_single_quotes(tmp_path: Path) -> None:
    """Test parsing JSON that uses single quotes instead of double quotes."""
    # Note: our current parse_agent_output uses json.loads, which is strict.
    raw_content_single_quoted = "{'agent': 'balthasar', 'verdict': 'reject'}"

    raw_json_case1 = {
        "response": f"```json\n{raw_content_single_quoted}\n```",
        "stats": {},
    }
    raw_file_case1 = tmp_path / "raw_case1.json"
    parsed_file_case1 = tmp_path / "parsed_case1.json"
    with open(raw_file_case1, "w") as f:
        json.dump(raw_json_case1, f)

    with pytest.raises(Exception):
        parse_agent_output(str(raw_file_case1), str(parsed_file_case1))


def test_parse_json_with_nested_structures(tmp_path: Path) -> None:
    """Test parsing JSON with nested objects and arrays."""
    raw_json = {
        "response": """```json
{
  "agent": "melchior",
  "verdict": "approve",
  "confidence": 0.9,
  "summary": "Nested data processed",
  "reasoning": "Complex structure handled",
  "findings": [
    {
      "severity": "info",
      "title": "Nested Finding",
      "detail": "Details here",
      "sources": ["melchior", {"nested_obj": "value"}],
      "nested_array": [1, 2, {"key": "val"}]
    }
  ],
  "recommendation": "Proceed"
}
```""",
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)

    assert data["agent"] == "melchior"
    assert data["verdict"] == "approve"
    assert isinstance(data["findings"], list)
    assert len(data["findings"]) == 1
    finding = data["findings"][0]
    assert finding["severity"] == "info"
    assert finding["sources"] == ["melchior", {"nested_obj": "value"}]
    assert finding["nested_array"] == [1, 2, {"key": "val"}]


def test_parse_output_with_semantically_off_but_valid_json(tmp_path: Path) -> None:
    """Test parsing valid JSON that might be semantically unexpected."""
    raw_json = {
        "response": """```json
{
  "agent": "balthasar",
  "verdict": "approve",
  "confidence": "0.95",
  "summary": "Confidence as string",
  "reasoning": "This should be parsed correctly as a string",
  "findings": [],
  "recommendation": "OK"
}
```""",
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)

    assert data["agent"] == "balthasar"
    assert data["verdict"] == "approve"
    assert data["confidence"] == "0.95"


def test_parse_output_from_malformed_gemini_response(tmp_path: Path) -> None:
    """Test cases where Gemini CLI might return malformed top-level JSON."""
    malformed_response_text = "This is not JSON output."
    raw_file_text = tmp_path / "raw_malformed_text.json"
    parsed_file_text = tmp_path / "parsed_malformed_text.json"
    with open(raw_file_text, "w") as f:
        f.write(json.dumps({"response": malformed_response_text, "stats": {}}))

    with pytest.raises(Exception):
        parse_agent_output(str(raw_file_text), str(parsed_file_text))

    malformed_response_json = {
        "response": "This is not JSON, but it is inside a response field.",
        "stats": {},
    }
    raw_file_json = tmp_path / "raw_malformed_json.json"
    parsed_file_json = tmp_path / "parsed_malformed_json.json"
    with open(raw_file_json, "w") as f:
        json.dump(malformed_response_json, f)

    with pytest.raises(Exception):
        parse_agent_output(str(raw_file_json), str(parsed_file_json))
