from __future__ import annotations

from analyzer.failure_classifier import FailureReport
from tasks.models import TaskRecord


def inject_hint(task: TaskRecord, report: FailureReport) -> None:
    """
    Augment task.prompt with a targeted hint based on where reasoning broke down.

    Mutates task.prompt in place so the next run picks up the improved instructions.
    """
    raise NotImplementedError


def rewrite_failing_step(task: TaskRecord, step_index: int, new_instruction: str) -> None:
    """
    Replace the instruction for a specific step that repeatedly fails.

    Useful when a single action (e.g. "click the submit button") is phrased
    in a way the agent consistently misinterprets.
    """
    raise NotImplementedError
