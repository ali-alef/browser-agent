from __future__ import annotations

from typing import Literal

import pydantic


class TaskRecord(pydantic.BaseModel):
    """Task definition only - execution results stored separately in storage/"""
    id: int | str
    prompt: str
    level: Literal["easy", "medium", "hard", "very_hard"]

    @pydantic.field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("prompt cannot be empty")
        return v


class TaskList(pydantic.RootModel[list[TaskRecord]]):
    pass
