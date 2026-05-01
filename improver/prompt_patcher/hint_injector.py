from __future__ import annotations

from analyzer.failure_classifier import FailureReport
from tasks.models import TaskRecord


def inject_hint(task: TaskRecord, report: FailureReport) -> None:
    """
    Augment task.prompt with a targeted hint based on where reasoning broke down.

    Mutates task.prompt in place so the next run picks up the improved instructions.
    """
    hints = []

    # Analyze evidence to generate specific hints
    for evidence in report.evidence:
        if "looping" in evidence.lower():
            hints.append(
                "\n[HINT] You seem to be repeating the same action. "
                "Try a different approach or scroll to find alternative elements."
            )
        elif "hallucinated" in evidence.lower() or "selector" in evidence.lower():
            hints.append(
                "\n[HINT] The element you're trying to click might not exist. "
                "Take a screenshot and carefully inspect the page structure before clicking."
            )
        elif "not visible" in evidence.lower():
            hints.append(
                "\n[HINT] The element exists but may be hidden or outside the viewport. "
                "Try scrolling or expanding sections to make it visible."
            )
        elif "misread" in evidence.lower():
            hints.append(
                "\n[HINT] Re-read the task carefully and ensure your actions align with it. "
                "Current task is: " + task.prompt.split('\n')[0]
            )

    # Only add hints once (avoid duplicating them)
    if hints and "[HINT]" not in task.prompt:
        task.prompt += "\n\n" + "".join(hints)

        # Track the improvement
        task.improvement_history.append({
            "type": "prompt_hint",
            "reason": report.failure_type,
            "hints_added": len(hints),
        })
