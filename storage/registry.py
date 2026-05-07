from __future__ import annotations

import json

from analyzer import models as analyzer_models
from runner import models as runner_models
from improver import models as improver_models


def load_run_record(task_id: str, run_id: str) -> runner_models.Run:
    filename = f"task_{task_id}_{run_id}.json"
    with open(f"storage/runs/{filename}", mode="r") as run_file:
        return runner_models.Run.model_validate(json.load(run_file))


def save_run_record(run_record: runner_models.Run) -> None:
    filename = f"task_{run_record.task_id}_{run_record.run_id}.json"
    with open(f"storage/runs/{filename}", mode="w", encoding="utf-8") as run_file:
        json.dump(
            run_record.model_dump(mode="json", serialize_as_any=True),
            run_file,
            indent=2,
            ensure_ascii=False,
        )


def load_analysis_record(task_id: str, run_id: str) -> analyzer_models.RunAnalysis:
    filename = f"analys_{task_id}_{run_id}.json"
    with open(f"storage/analys/{filename}", mode="r") as run_file:
        return analyzer_models.RunAnalysis.model_validate(json.load(run_file))


def save_analysis_record(run_analyze: analyzer_models.RunAnalysis) -> None:
    filename = f"analys_{run_analyze.task_id}_{run_analyze.run_id}.json"
    with open(f"storage/analys/{filename}", mode='w', encoding="utf-8") as analys_file:
        json.dump(
            run_analyze.model_dump(mode="json", serialize_as_any=True),
            analys_file,
            indent=2,
            ensure_ascii=False,
        )


def save_improvement_plan(improvement_plan: improver_models.ImprovementPlan) -> None:
    filename = f"improve_{improvement_plan.task_id}_{improvement_plan.analysis_run_id}.json"
    with open(f"storage/improvements/{filename}", mode='w', encoding="utf-8") as improve_file:
        json.dump(
            improvement_plan.model_dump(mode="json", serialize_as_any=True),
            improve_file,
            indent=2,
            ensure_ascii=False,
        )
