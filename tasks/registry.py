from __future__ import annotations

import json

from tasks import models as task_models


def load_task(task_id: str) -> task_models.TaskRecord:
    with open(f"tasks/definitions/task_{task_id}.json", encoding="utf-8") as task_file:
        return task_models.TaskRecord.model_validate(json.load(task_file))
