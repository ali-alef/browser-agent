from __future__ import annotations

from typing import Any

import pydantic


class Step(pydantic.BaseModel):
    """Minimal step record containing only data needed for analysis and improvement."""
    type: str  # "action", "observation", "thought", "navigation"
    status: str = "pending"  # "success", "failed", "pending"
    reason: str = ""  # Why it failed
    error: str = ""  # Error message
    content: str = ""  # Content/observation/thought text
    action_type: str = ""  # Type of action (click, type, scroll, navigate)
    target: str = ""  # CSS selector or element identifier

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for backward compatibility with analyzer."""
        return getattr(self, key, default)


class Run(pydantic.BaseModel):
    """Execution record for a single task attempt."""
    run_id: str
    task_id: str | int
    agent_version: str = ""
    steps: list[Step] = pydantic.Field(default_factory=list)
    final_status: str = "pending"  # pending | completed | failed | timed_out
    final_output: str = ""
    failure_category: str | None = None
