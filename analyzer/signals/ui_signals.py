from __future__ import annotations

import re
from typing import Any


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of site UI problems in the step trace.

    Examples to detect: overlapping/hidden elements, missing labels,
    confusing selectors, layout shifts, CAPTCHA walls, broken navigation.

    Returns a list of human-readable evidence strings.
    """
    evidence = []

    for i, step in enumerate(step_trace):
        # Check for failed element detection
        if step.get("type") == "action" and step.get("status") == "failed":
            reason = step.get("reason", "")
            if "selector" in reason.lower() or "element" in reason.lower():
                evidence.append(f"Step {i}: Element not found - {reason}")
            if "visible" in reason.lower():
                evidence.append(f"Step {i}: Element not visible/clickable - {reason}")

        # Check for CAPTCHA detection
        if "captcha" in str(step).lower():
            evidence.append(f"Step {i}: CAPTCHA detected")

        # Check for network/timeout errors
        if "timeout" in str(step).lower():
            evidence.append(f"Step {i}: Timeout during action")
        if "network" in str(step).lower() or "connection" in str(step).lower():
            evidence.append(f"Step {i}: Network error detected")

        # Check for repeated failed attempts at same element
        if i > 0:
            prev_step = step_trace[i - 1]
            if (
                step.get("type") == "action"
                and prev_step.get("type") == "action"
                and step.get("target") == prev_step.get("target")
                and step.get("status") == "failed"
                and prev_step.get("status") == "failed"
            ):
                evidence.append(f"Step {i}: Repeated failure on same element")

        # Check for page errors
        if step.get("type") == "observation":
            observation = step.get("content", "")
            if "error" in observation.lower() and "page" in observation.lower():
                evidence.append(f"Step {i}: Page error observed")

    return evidence
