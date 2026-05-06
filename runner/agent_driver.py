from __future__ import annotations

import browser_use

from runner import models as runner_models
from runner import serializer as runner_serializer
from tasks import models as task_models
from storage import registry as storage_registry
import settings


async def run_one_task(task: task_models.TaskRecord) -> runner_models.Run:
    agent_kwargs = {
        "task": task.prompt.strip(),
        "llm": browser_use.llm.ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.MODEL_API_KEY,
            base_url=settings.MODEL_URL,
        ),
        "task_id": str(task.id),
    }
    if settings.SOCKS5_PROXY:
        agent_kwargs["browser"] = browser_use.Browser(
            proxy=browser_use.browser.ProxySettings(server=settings.SOCKS5_PROXY)
        )
    agent = browser_use.Agent(**agent_kwargs)

    history = await agent.run()
    run_record = runner_serializer.serialize_run(task, history)
    storage_registry.save_run_record(run_record)
    return run_record
