from __future__ import annotations

from typing import Any


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of agent/LLM reasoning failures in the step trace.

    Examples to detect: repeated identical actions (looping), hallucinated
    selectors, misread task instructions, premature task abandonment,
    broken reasoning chain.

    Returns a list of human-readable evidence strings.
    """
    raise NotImplementedError
