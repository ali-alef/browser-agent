from __future__ import annotations

import browser_use

from runner.llm.copilot_model import ChatCopilotCLI
from tasks.models import TaskRecord


async def run_one_task(task: TaskRecord) -> None:
    task.status = "running"
    task.failure_category = None
    task.final_output = ""
    task.step_trace = []

    try:
        agent = browser_use.Agent(
            task=task.prompt.strip(),
            llm=ChatCopilotCLI(model=task.model),
            task_id=str(task.id),
            browser=browser_use.Browser(
                proxy=browser_use.browser.ProxySettings(server="socks5://localhost:2080")
            ),
        )
        history = await agent.run()

        task.step_trace = history.model_dump().get("history", [])
        task.final_output = history.final_result() or ""

        # TODO: Replace with proper failure_classifier once analyzer/ is implemented.
        if history.is_successful() and history.is_done():
            task.status = "completed"
        elif not history.is_successful():
            task.status = "failed"
            task.failure_category = "agent_unsuccessful"
            task.status = "completed"
        else:
            task.status = "failed"
            task.failure_category = "agent_incomplete"

    except Exception as exc:
        task.status = "failed"
        task.failure_category = type(exc).__name__
        task.final_output = str(exc)
