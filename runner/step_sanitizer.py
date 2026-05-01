from __future__ import annotations

from typing import Any

from runner.session import Step


def sanitize_history(raw_history: list[dict[str, Any]]) -> list[Step]:
    """
    Extract only essential fields from raw browser_use history.
    
    Drops: screenshots, DOM dumps, full responses, timestamps, memory info, etc.
    Keeps: type, status, reason, error, content, action_type, target
    
    These minimal fields are sufficient for:
    - Analyzer: Detecting UI, LLM, and environment failures
    - Improver: Generating hints and UI patches
    """
    sanitized = []
    
    for raw_step in raw_history:
        # Extract only the fields we need
        step = Step(
            type=_get_str(raw_step, ["type"], "unknown"),
            status=_get_str(raw_step, ["status"], "pending"),
            reason=_get_str(raw_step, ["reason"], ""),
            error=_get_str(raw_step, ["error"], ""),
            content=_get_str(raw_step, ["content", "observation", "thought"], ""),
            action_type=_get_str(raw_step, ["action_type", "action"], ""),
            target=_get_str(raw_step, ["target", "element", "selector"], ""),
        )
        sanitized.append(step)
    
    return sanitized


def _get_str(obj: dict[str, Any], keys: list[str], default: str = "") -> str:
    """
    Try to extract a string value from dict using multiple possible keys.
    Returns default if not found or is None.
    """
    for key in keys:
        value = obj.get(key)
        if value is not None:
            return str(value).strip()
    return default
