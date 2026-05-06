from __future__ import annotations

import argparse
import asyncio

from analyzer import failure_classifier
from runner import agent_driver
from tasks import registry as task_registry

async def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", type=int, help="Task ID")
    args = parser.parse_args()

    task = task_registry.load_task(args.task_id)
    run_record = await agent_driver.run_one_task(task)
    failure_classifier.analyze(run_record)


if __name__ == "__main__":
    asyncio.run(_main())
