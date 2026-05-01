from __future__ import annotations

from uuid import uuid4

import browser_use

from tasks.models import TaskRecord
from storage.executor import save_run_record
from runner.session import Run
from runner.step_sanitizer import sanitize_history


async def run_one_task(task: TaskRecord) -> Run:
    run_record = Run(
        run_id=str(uuid4()),
        task_id=task.id,
        agent_version="gemini-2.5-flash",
    )

    try:
        agent = browser_use.Agent(
            task=task.prompt.strip(),
            llm=browser_use.llm.ChatGoogle(
                model="gemini-2.5-flash",
                api_key="AIzaSyBQmtjOcORblJY28moMGEVQkgqnGriFBM0",
            ),
            task_id=str(task.id),
            browser=browser_use.Browser(
                proxy=browser_use.browser.ProxySettings(server="socks5://localhost:2080")
            ),
        )
        history = await agent.run()

        # Extract and sanitize steps to keep only essential fields
        raw_steps = history.model_dump().get("history", [])
        run_record.steps = sanitize_history(raw_steps)
        run_record.final_output = history.final_result() or ""

        if history.is_successful() and history.is_done():
            run_record.final_status = "completed"
        elif not history.is_successful():
            run_record.final_status = "failed"
            run_record.failure_category = "agent_unsuccessful"
        else:
            run_record.final_status = "failed"
            run_record.failure_category = "agent_incomplete"

    except Exception as exc:
        run_record.final_status = "failed"
        run_record.failure_category = type(exc).__name__
        run_record.final_output = str(exc)

    save_run_record(run_record)

    return run_record
