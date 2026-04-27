from __future__ import annotations

from analyzer.failure_classifier import FailureReport, FailureType
from tasks.models import TaskRecord


def apply_improvement(task: TaskRecord, report: FailureReport) -> bool:
    """
    Dispatch to the right improver based on the failure type.

    Returns True if an improvement was applied (so the caller can re-run),
    False if no applicable fix was found.
    """
    handlers: dict[FailureType, object] = {
        "site_ui": _fix_ui,
        "agent_reasoning": _fix_prompt,
        "environment": _fix_env,
        "ambiguous": _fix_ambiguous,
    }
    handler = handlers.get(report.failure_type)
    if handler is None:
        return False
    return handler(task, report)  # type: ignore[operator]


def _fix_ui(task: TaskRecord, report: FailureReport) -> bool:
    raise NotImplementedError


def _fix_prompt(task: TaskRecord, report: FailureReport) -> bool:
    raise NotImplementedError


def _fix_env(task: TaskRecord, report: FailureReport) -> bool:
    raise NotImplementedError


def _fix_ambiguous(task: TaskRecord, report: FailureReport) -> bool:
    raise NotImplementedError
