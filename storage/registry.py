from __future__ import annotations

import json
from pathlib import Path

from analyzer import models as analyzer_models
from runner import models as runner_models

STORAGE_DIR = Path(__file__).parent


def save_run_record(run_record: runner_models.Run) -> None:
    filename = f"task_{run_record.task_id}_{run_record.run_id}.json"
    with open(f"storage/runs/{filename}", mode="w", encoding="utf-8") as run_file:
        json.dump(
            run_record.model_dump(mode="json", serialize_as_any=True),
            run_file,
            indent=2,
            ensure_ascii=False,
        )

def save_analysis_record(run_analyze: analyzer_models.RunAnalysis) -> None:
    filename = f"analys_{run_analyze.task_id}_{run_analyze.run_id}.json"
    with open(f"storage/analys/{filename}", mode='w', encoding="utf-8") as analys_file:
        json.dump(
            run_analyze.model_dump(mode="json", serialize_as_any=True),
            analys_file,
            indent=2,
            ensure_ascii=False,
        )
