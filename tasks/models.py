from __future__ import annotations

from typing import Literal

import pydantic


class TaskRecord(pydantic.BaseModel):
    id: int
    prompt: str
    level: Literal["easy", "medium", "hard", "very_hard"]
    hints: list[str] = pydantic.Field(default_factory=list)
    step_guidance: dict[int | str, str] = pydantic.Field(default_factory=dict)
