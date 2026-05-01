from __future__ import annotations

import json
from pathlib import Path

from runner.session import Run

STORAGE_DIR = Path(__file__).parent


def save_run_record(run_record: Run) -> str:
    runs_dir = STORAGE_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    filename = f"task_{run_record.task_id}_{run_record.run_id}.json"
    filepath = runs_dir / filename

    payload = run_record.model_dump(mode="json", serialize_as_any=True)
    filepath.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    return str(filepath)

def save_improvement_prompt(task_id: int | str, improved_prompt: str) -> str:
    """Save improved prompt to storage/improvements/{task_id}_prompt.txt"""
    improvements_dir = STORAGE_DIR / "improvements"
    improvements_dir.mkdir(parents=True, exist_ok=True)

    filepath = improvements_dir / f"task_{task_id}_prompt.txt"
    filepath.write_text(improved_prompt, encoding="utf-8")

    return str(filepath)
