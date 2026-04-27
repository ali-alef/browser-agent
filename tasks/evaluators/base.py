from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from tasks.models import TaskRecord


@dataclass
class EvaluationResult:
    passed: bool
    reason: str
    details: dict[str, Any] = field(default_factory=dict)


class BaseEvaluator(Protocol):
    def evaluate(self, task: TaskRecord) -> EvaluationResult: ...
