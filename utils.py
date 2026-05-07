"""Utility functions for common operations across modules."""

from __future__ import annotations


def extract_json_object(text: str) -> str:
    """Extract a JSON object from text that may contain other content.
    
    Handles several formats:
    - Pure JSON: "{...}"
    - Markdown code block: "```json\n{...}\n```"
    - Embedded JSON: "Some text... {...} ... more text"
    
    Args:
        text: The text to extract JSON from
        
    Returns:
        The extracted JSON string
        
    Raises:
        RuntimeError: If no valid JSON object can be found
    """
    stripped = text.strip()
    
    # Case 1: Pure JSON
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    
    # Case 2: Markdown code block
    if "```json" in stripped:
        start = stripped.find("```json")
        end = stripped.find("```", start + 7)
        if end != -1:
            candidate = stripped[start + 7 : end].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate
    
    # Case 3: Embedded JSON (greedy from first { to last })
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first != -1 and last != -1 and last > first:
        return stripped[first : last + 1]
    
    raise RuntimeError("No JSON object found in text.")
