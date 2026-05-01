from __future__ import annotations

from typing import Any
from collections import defaultdict


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of agent/LLM reasoning failures in the step trace.

    Examples to detect: repeated identical actions (looping), hallucinated
    selectors, misread task instructions, premature task abandonment,
    broken reasoning chain.

    Returns a list of human-readable evidence strings.
    """
    evidence = []
    action_history = defaultdict(int)

    for i, step in enumerate(step_trace):
        # Check for action loops (same action repeated)
        if step.get("type") == "action":
            action_key = (
                step.get("action_type"),
                step.get("target"),
                step.get("content")
            )
            action_history[action_key] += 1

            if action_history[action_key] > 2:
                evidence.append(
                    f"Step {i}: Repeated action detected (looping) - "
                    f"{step.get('action_type')} on {step.get('target')}"
                )

        # Check for hallucinated selectors (selectors that don't exist)
        if step.get("type") == "action" and step.get("status") == "failed":
            if "selector" in step.get("error", "").lower():
                evidence.append(
                    f"Step {i}: Hallucinated selector - "
                    f"'{step.get('target')}' does not exist"
                )

        # Check for contradictory reasoning
        if step.get("type") == "thought":
            thought = step.get("content", "")
            if "done" in thought.lower() and i < len(step_trace) - 3:
                # If agent says it's done but there are more steps, reasoning is broken
                if len([s for s in step_trace[i:] if s.get("type") == "action"]) > 0:
                    evidence.append(
                        f"Step {i}: Agent claims task done but continues with actions"
                    )

        # Check for misread instructions
        if step.get("type") == "action":
            action_content = str(step.get("content", "")).lower()
            # Look for contradictory search terms or misunderstandings
            if (
                i > 0
                and step_trace[0].get("type") == "thought"
            ):
                instruction = step_trace[0].get("content", "").lower()
                if (
                    "search" in instruction
                    and "navigate" in action_content
                    and "search" not in action_content
                ):
                    evidence.append(
                        f"Step {i}: Task is to search, but agent navigated instead"
                    )

    return evidence
