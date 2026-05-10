import json
import os
import re
import sys

# centralize size limit here too
MAX_INPUT_FILE_SIZE = 10 * 1024 * 1024

_FENCE_START = re.compile(r"^```(?:json)?\s*\n?", re.IGNORECASE)
_FENCE_END = re.compile(r"\n?```\s*$")

def _strip_code_fences(text: str) -> str:
    text = text.strip()
    text = _FENCE_START.sub("", text)
    text = _FENCE_END.sub("", text)
    return text.strip()

def _extract_text(data: object) -> str:
    # Gemini CLI output format: {"response": "...", "stats": {...}}
    if isinstance(data, dict) and "response" in data:
        return str(data["response"])
    
    # Fallback to original Claude shapes if needed
    if isinstance(data, dict) and "result" in data:
        return str(data["result"])

    if isinstance(data, dict) and "content" in data:
        content = data["content"]
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return str(block["text"])
        raise ValueError("No text block found in 'content' array")

    if isinstance(data, str):
        return data

    raise ValueError(f"Unexpected output type: {type(data).__name__}")

def parse_agent_output(input_path: str, output_path: str) -> None:
    file_size = os.path.getsize(input_path)
    if file_size > MAX_INPUT_FILE_SIZE:
        raise ValueError(f"Input file {input_path} too large.")

    with open(input_path, encoding="utf-8") as fh:
        data = json.load(fh)

    text = _extract_text(data)
    text = _strip_code_fences(text)

    parsed = json.loads(text)

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(parsed, fh, indent=2)
        fh.write("\n")
