import json
from pathlib import Path
from typing import Any

import pydantic


TASKS_PATH = Path(__file__).with_name("tasks.json")

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


def load_tasks(path: Path = TASKS_PATH) -> list[TaskRecord]:
    return TaskList.model_validate_json(path.read_text(encoding="utf-8")).root


def save_tasks(tasks: list[TaskRecord], path: Path = TASKS_PATH) -> None:
    payload = TaskList(tasks).model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
