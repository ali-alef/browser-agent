from __future__ import annotations

import sys

from tasks.registry import load_tasks
from runner.agent_driver import run_one_task

MAX_RETRIES = 1


async def run_pipeline_for_task(task) -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  Attempt {attempt}/{MAX_RETRIES}...")

        await run_one_task(task)

    print(f"    Task {task.id} completed.")


async def main() -> None:
    tasks = load_tasks()

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        target_id = int(sys.argv[1])
        for task in tasks:
            if task.id == target_id:
                print(f"Running task {task.id}...")
                await run_pipeline_for_task(task)
        return

    print("No task ID provided.")
