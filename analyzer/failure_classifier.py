from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from tasks.models import TaskRecord

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
    raise NotImplementedError
