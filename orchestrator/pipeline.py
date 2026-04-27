from __future__ import annotations

import asyncio
import sys

from tasks.registry import load_tasks, save_tasks
from runner.agent_driver import run_one_task
from tasks.evaluators.base import EvaluationResult

MAX_RETRIES = 3


async def run_pipeline_for_task(task) -> None:
    """Run one task through the full evaluate → analyze → improve feedback loop."""
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  Attempt {attempt}/{MAX_RETRIES}...")
        await run_one_task(task)

        if task.status == "completed":
            print(f"  Task {task.id} succeeded.")
            return

        # TODO: plug in failure_classifier and improver once implemented.
        # report = failure_classifier.classify(task)
        # improved = improver.router.apply_improvement(task, report)
        # if not improved:
        #     print(f"  No applicable fix found for task {task.id}.")
        #     return
        # task.status = "pending"  # reset for next attempt

        print(f"  Task {task.id} failed (category={task.failure_category}). No improver wired yet.")
        return

    print(f"  Task {task.id} exhausted {MAX_RETRIES} retries.")


async def main() -> None:
    tasks = load_tasks()

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        target_id = int(sys.argv[1])
        for task in tasks:
            if task.id == target_id:
                print(f"Running task {task.id}...")
                await run_pipeline_for_task(task)
                save_tasks(tasks)
        return

    print("No task ID provided — running all pending tasks.")
    pending = [t for t in tasks if t.status == "pending"]
    if not pending:
        print("No pending tasks found.")
        return

    for task in pending:
        print(f"Running task {task.id}...")
        await run_pipeline_for_task(task)
        save_tasks(tasks)
