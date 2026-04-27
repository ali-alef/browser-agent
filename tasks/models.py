from __future__ import annotations

from typing import Any

import pydantic


class TaskRecord(pydantic.BaseModel):
    id: int | str
    prompt: str
    model: str = "gpt-5.3-codex"
    status: str = "pending"
    step_trace: list[dict[str, Any]] = pydantic.Field(default_factory=list)
    final_output: str = ""
    failure_category: str | None = None

    @pydantic.field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("prompt cannot be empty")
        return v


class TaskList(pydantic.RootModel[list[TaskRecord]]):
    pass
