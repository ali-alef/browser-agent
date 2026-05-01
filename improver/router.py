from __future__ import annotations

from analyzer.failure_classifier import FailureReport, FailureType
from tasks.models import TaskRecord
from improver.prompt_patcher import hint_injector
from improver.ui_patcher import patch_generator


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
    """Generate and apply UI patches to improve element accessibility."""
    patch = patch_generator.generate(report)
    if patch is None:
        return False

    patch_generator.apply(patch, task)
    return True


def _fix_prompt(task: TaskRecord, report: FailureReport) -> bool:
    """Inject hints to improve agent reasoning."""
    # Only inject hints if confidence is high enough
    if report.confidence < 0.4:
        return False

    hint_injector.inject_hint(task, report)
    return True


def _fix_env(task: TaskRecord, report: FailureReport) -> bool:
    """
    Handle environment failures.

    Most environment failures (network, auth, third-party blocks) require
    manual intervention or retry logic, not code changes.
    """
    # Log the environment issue but don't apply a fix
    task.improvement_history.append({
        "type": "env_issue_noted",
        "reason": report.suggested_fix_area,
        "evidence": report.evidence[:2],  # First 2 pieces of evidence
    })
    # Return False to indicate no automatic fix was applied
    return False


def _fix_ambiguous(task: TaskRecord, report: FailureReport) -> bool:
    """For ambiguous failures, try prompt injection as a fallback."""
    # Only try if we have some evidence
    if not report.evidence:
        return False

    hint_injector.inject_hint(task, report)
    return True
