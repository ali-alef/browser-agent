from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Run:
    run_id: str
    task_id: str | int
    agent_version: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    final_status: str = "pending"  # pending | completed | failed | timed_out
    final_output: str = ""
    failure_category: str | None = None
