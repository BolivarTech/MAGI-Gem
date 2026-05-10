import json
from pathlib import Path
from parse_agent_output import parse_agent_output


def test_parse_gemini_wrapped_json(tmp_path: Path) -> None:
    """Test parsing the new Gemini CLI output format."""
    raw_json = {
        "response": '```json
{"agent": "melchior", "verdict": "approve", "confidence": 1.0, "summary": "OK", "reasoning": "...", "findings": [], "recommendation": "..."}
```',
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
        "response": '  ```json  
 { 
 "agent": "caspar" ,
 "verdict" : "approve"
 }
 ```  ',
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
        "response": '```json
{"agent": "melchior", "verdict": "approve", "summary": "OK
with	tabs", "reasoning": "...", "findings": [], "recommendation": "..."}
```',
        "stats": {},
    }
    raw_file = tmp_path / "raw.json"
    parsed_file = tmp_path / "parsed.json"

    with open(raw_file, "w") as f:
        json.dump(raw_json, f)

    parse_agent_output(str(raw_file), str(parsed_file))

    with open(parsed_file, "r") as f:
        data = json.load(f)
    assert data["summary"] == "OK
with	tabs"


def test_parse_json_with_single_quotes(tmp_path: Path) -> None:
    """Test parsing JSON that uses single quotes instead of double quotes (which is technically invalid JSON but might be encountered)."""
    # Note: json.loads strictly requires double quotes for keys and strings.
    # This test assumes the underlying parser (or a more lenient one) might handle it.
    # However, our current parse_agent_output uses json.loads, so this test is more about documenting behavior.
    # If the requirement is strict JSON, this might fail as expected.
    # The current implementation uses json.loads which will raise an error.
    # We expect a JSONDecodeError to be caught and potentially handled by fallback.
    raw_json_invalid = {
        "response": "'{"agent": "balthasar", "verdict": "reject"}'", # Raw response has single quotes around JSON string
        "stats": {},
    }
    raw_file_invalid = tmp_path / "raw_invalid_quotes.json"
    parsed_file_invalid = tmp_path / "parsed_invalid_quotes.json"

    with open(raw_file_invalid, "w") as f:
        json.dump(raw_json_invalid, f)

    # The parse_agent_output attempts to load the response content as JSON.
    # If the response content itself is not valid JSON (e.g., single quotes), json.loads will fail.
    # The current logic might fall back to loading the raw text if JSON parsing fails.
    # Let's test the behavior where the *content* is invalid JSON.
    raw_content_invalid_json = '{"agent": "balthasar", "verdict": "reject"}' # Valid JSON
    raw_content_single_quoted = "{'agent': 'balthasar', 'verdict': 'reject'}" # Invalid JSON

    # Case 1: Response contains valid JSON string, but it's wrapped in single quotes as part of the 'response' value
    raw_json_case1 = {
        "response": f'```json
{raw_content_single_quoted}
```',
        "stats": {},
    }
    raw_file_case1 = tmp_path / "raw_case1.json"
    parsed_file_case1 = tmp_path / "parsed_case1.json"
    with open(raw_file_case1, "w") as f:
        json.dump(raw_json_case1, f)

    # Expecting this to fail during json.loads(json_text) because json_text will be "{'agent': 'balthasar', 'verdict': 'reject'}"
    with pytest.raises(Exception) as excinfo: # Catching a general Exception because json.loads might raise different types
         parse_agent_output(str(raw_file_case1), str(parsed_file_case1))

    # The parse_agent_output has a fallback that tries to load the raw text if extraction fails.
    # If the raw text itself is still not valid JSON, it will fail.
    # For this specific test, single quotes will cause json.loads to fail even in fallback.
    assert "Invalid JSON" in str(excinfo.value) or "No JSON object could be decoded" in str(excinfo.value)


def test_parse_json_with_nested_structures(tmp_path: Path) -> None:
    """Test parsing JSON with nested objects and arrays."""
    raw_json = {
        "response": '```json
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
```',
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
    """Test parsing valid JSON that might be semantically unexpected (e.g., wrong types in fields not strictly validated by json.loads)."""
    # This tests the parsing stage, not the validation stage which happens later.
    # For example, a number might be expected but a string is provided, if json.loads accepts it.
    raw_json = {
        "response": '```json
{
  "agent": "balthasar",
  "verdict": "approve",
  "confidence": "0.95",
  "summary": "Confidence as string",
  "reasoning": "This should be parsed correctly as a string",
  "findings": [],
  "recommendation": "OK"
}
```',
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
    # The confidence is a string here, which json.loads accepts. Validation stage would catch this.
    assert data["confidence"] == "0.95"
    assert isinstance(data["confidence"], str)


def test_parse_output_from_malformed_gemini_response(tmp_path: Path) -> None:
    """Test cases where Gemini CLI might return malformed top-level JSON."""
    # Case 1: Gemini response is just text, not JSON
    malformed_response_text = "This is not JSON output."
    raw_file_text = tmp_path / "raw_malformed_text.json"
    parsed_file_text = tmp_path / "parsed_malformed_text.json"
    with open(raw_file_text, "w") as f:
        f.write(json.dumps({"response": malformed_response_text, "stats": {}}))

    # parse_agent_output first tries to load the whole file as JSON, then extracts 'response', then parses 'response'.
    # If 'response' is not JSON, it falls back to loading the raw text.
    # In this case, the raw text IS NOT JSON. So it should fail.
    with pytest.raises(Exception) as excinfo: # Catching general exception as json.loads might raise various types
        parse_agent_output(str(raw_file_text), str(parsed_file_text))
    assert "Invalid JSON" in str(excinfo.value) or "No JSON object could be decoded" in str(excinfo.value)

    # Case 2: Gemini response is JSON, but 'response' field is not valid JSON
    malformed_response_json = {
        "response": "This is not JSON, but it is inside a response field.",
        "stats": {},
    }
    raw_file_json = tmp_path / "raw_malformed_json.json"
    parsed_file_json = tmp_path / "parsed_malformed_json.json"
    with open(raw_file_json, "w") as f:
        json.dump(malformed_response_json, f)

    # parse_agent_output will load the malformed_response_json, extract the 'response' string,
    # attempt to parse it as JSON (which will fail), then fallback to loading the raw string itself as JSON.
    # Since "This is not JSON..." is not valid JSON, this should also fail.
    with pytest.raises(Exception) as excinfo:
        parse_agent_output(str(raw_file_json), str(parsed_file_json))
    assert "Invalid JSON" in str(excinfo.value) or "No JSON object could be decoded" in str(excinfo.value)
