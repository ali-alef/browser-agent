from __future__ import annotations

import json
from pathlib import Path

from tasks.models import TaskList, TaskRecord

TASKS_PATH = Path(__file__).parent / "definitions" / "tasks.json"


def load_tasks(path: Path = TASKS_PATH) -> list[TaskRecord]:
    return TaskList.model_validate_json(path.read_text(encoding="utf-8")).root


def save_tasks(tasks: list[TaskRecord], path: Path = TASKS_PATH) -> None:
    payload = TaskList(tasks).model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
