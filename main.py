from __future__ import annotations

import argparse
import asyncio

from analyzer import failure_classifier
from runner import agent_driver
from storage import registry as storage_registry
from tasks import registry as task_registry
from improver import improvement_engine

def analyze_run(task_id: str, run_id: str) -> None:
    run = storage_registry.load_run_record(task_id=task_id, run_id=run_id)
    failure_classifier.analyze(run)


def improve_run(task_id: str, run_id: str) -> None:
    analys = storage_registry.load_analysis_record(task_id=task_id, run_id=run_id)
    improvement_engine.generate_improvement_plan(analys)


async def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", type=int, help="Task ID")
    args = parser.parse_args()

    task = task_registry.load_task(args.task_id)
    run_record = await agent_driver.run_one_task(task)
    failure_classifier.analyze(run_record)


if __name__ == "__main__":
    # asyncio.run(_main())
    improve_run("1", "9e1b894d-dc0a-4d28-a29a-baf79b57748c")
