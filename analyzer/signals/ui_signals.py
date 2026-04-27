from __future__ import annotations

from typing import Any


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of site UI problems in the step trace.

    Examples to detect: overlapping/hidden elements, missing labels,
    confusing selectors, layout shifts, CAPTCHA walls, broken navigation.

    Returns a list of human-readable evidence strings.
    """
    raise NotImplementedError
