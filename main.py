from __future__ import annotations

import argparse
import asyncio

from analyzer import failure_classifier
from runner import agent_driver
from storage import registry as storage_registry
from tasks import registry as task_registry
from improver import improvement_engine


async def run_task_workflow(task_id: str, previous_run_id: str) -> None:
    task = task_registry.load_task(task_id)

    improvement = None
    if previous_run_id:
        improvement = storage_registry.load_improvement(task_id, previous_run_id)

    print(f"\n📋 Running task {task_id}...")
    run_record = await agent_driver.run_one_task(task, improvement)
    print(f"✅ Task completed. Run ID: {run_record.run_id}")
    
    print(f"\n🔍 Analyzing run...")
    failure_classifier.analyze(run_record)
    analysis = storage_registry.load_analysis_record(str(task_id), run_record.run_id)
    print(f"📊 Analysis: {analysis.status.upper()}")
    if analysis.failure_report:
        print(f"   Failure Type: {analysis.failure_report.failure_type}")

    improvement_engine.generate_improvement_plan(analysis)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Browser Agent Task Runner")
    parser.add_argument("task_id", type=str, help="Task ID to run")
    parser.add_argument("previous_run_id", type=str, help="previous run ID for this task")
    
    args = parser.parse_args()
    
    await run_task_workflow(task_id=args.task_id, previous_run_id=args.previous_run_id)


if __name__ == "__main__":
    asyncio.run(_main())
