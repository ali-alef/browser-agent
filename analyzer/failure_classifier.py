from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from tasks.models import TaskRecord
from analyzer.signals import ui_signals, llm_signals, env_signals

FailureType = Literal["site_ui", "agent_reasoning", "environment", "ambiguous"]


@dataclass
class FailureReport:
    task_id: str | int
    failure_type: FailureType
    confidence: float  # 0.0 – 1.0
    evidence: list[str] = field(default_factory=list)
    suggested_fix_area: str = ""


def classify(task: TaskRecord) -> FailureReport:
    """Inspect a failed task's step_trace and determine the root cause."""

    # Collect evidence from all signal detectors
    ui_evidence = ui_signals.detect(task.step_trace)
    llm_evidence = llm_signals.detect(task.step_trace)
    env_evidence = env_signals.detect(task.step_trace)

    all_evidence = ui_evidence + llm_evidence + env_evidence

    # Determine failure type based on signal strength
    ui_score = len(ui_evidence)
    llm_score = len(llm_evidence)
    env_score = len(env_evidence)

    if env_score > 0 and env_score >= ui_score and env_score >= llm_score:
        failure_type: FailureType = "environment"
        confidence = min(1.0, env_score / 3.0)
        suggested_fix = "infrastructure_reset" if env_score > 2 else "retry_with_patience"

    elif ui_score > 0 and ui_score >= llm_score and ui_score >= env_score:
        failure_type = "site_ui"
        confidence = min(1.0, ui_score / 3.0)
        suggested_fix = "identify_selectors_from_trace"

    elif llm_score > 0 and llm_score >= ui_score and llm_score >= env_score:
        failure_type = "agent_reasoning"
        confidence = min(1.0, llm_score / 3.0)
        suggested_fix = "improve_task_prompt"

    else:
        failure_type = "ambiguous"
        confidence = 0.3
        suggested_fix = "manual_review_required"

    return FailureReport(
        task_id=task.id,
        failure_type=failure_type,
        confidence=confidence,
        evidence=all_evidence,
        suggested_fix_area=suggested_fix,
    )
