from __future__ import annotations

from tasks.models import TaskRecord


def print_summary(tasks: list[TaskRecord]) -> None:
    """Print a human-readable summary of task outcomes across a pipeline run."""
    raise NotImplementedError


def save_report(tasks: list[TaskRecord], output_path: str) -> None:
    """Persist a structured JSON report of all task outcomes and improvement cycles."""
    raise NotImplementedError
