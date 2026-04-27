from __future__ import annotations

from typing import Any


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of environment/infrastructure failures in the step trace.

    Examples to detect: network errors, authentication walls, third-party
    blocks, browser crashes, timeouts unrelated to the task itself.

    Returns a list of human-readable evidence strings.
    """
    raise NotImplementedError
