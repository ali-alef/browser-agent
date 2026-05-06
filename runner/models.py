from __future__ import annotations

from typing import Any

import pydantic


class Result(pydantic.BaseModel):
    error: str | None = None
    content: str | None = None


class Action(pydantic.BaseModel):
    type: str = "unknown"
    metadata: dict[str, Any] = pydantic.Field(default_factory=dict)


class Step(pydantic.BaseModel):
    step_number: int = 0
    actions: list[Action] = pydantic.Field(default_factory=list)
    results: list[Result] = pydantic.Field(default_factory=list)
    ai_input_message: str | None = None
    next_goal: str | None = None
    previous_goal: str | None = None
    memory: str | None = None
    thinking: str | None = None

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class Run(pydantic.BaseModel):
    run_id: str
    task_id: str | int
    task_prompt: str = ""
    agent_version: str = ""
    steps: list[Step] = pydantic.Field(default_factory=list)
    judgment: str = ""
    final_status: str = "pending"
    final_output: str = ""
