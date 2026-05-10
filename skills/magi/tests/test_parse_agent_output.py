import json
import pytest
from parse_agent_output import parse_agent_output

def test_parse_gemini_wrapped_json(tmp_path):
    """Test parsing the new Gemini CLI output format."""
    raw_json = {
        "response": '```json\n{"agent": "melchior", "verdict": "approve", "confidence": 1.0, "summary": "OK", "reasoning": "...", "findings": [], "recommendation": "..."}\n```',
        "stats": {}
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

def test_parse_raw_unfenced_json(tmp_path):
    """Test parsing if Gemini returns JSON without fences."""
    raw_json = {
        "response": '{"agent": "balthasar", "verdict": "reject", "confidence": 0.5, "summary": "No", "reasoning": "...", "findings": [], "recommendation": "..."}',
        "stats": {}
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
