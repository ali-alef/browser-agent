from __future__ import annotations

import os

import browser_use

from runner.serializer import serialize_run
from tasks.models import TaskRecord
from storage.executor import save_run_record

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_PROXY = "socks5://localhost:2080"

"AIzaSyDO-_y0LPDLToc4yxWfOvIlevph9TYpBfU"
"AIzaSyBQmtjOcORblJY28moMGEVQkgqnGriFBM0"

def _build_agent(task: TaskRecord) -> browser_use.Agent:
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBQmtjOcORblJY28moMGEVQkgqnGriFBM0")
    proxy = os.getenv("BROWSER_PROXY", DEFAULT_PROXY).strip()

    agent_kwargs = {
        "task": task.prompt.strip(),
        "llm": browser_use.llm.ChatOpenAI(
            model="gpt-4o",
            api_key="sk-tRFUVokeNnPpOsjoU0zlDw",
            base_url="http://34.72.104.120/",
        ),
        "task_id": str(task.id),
    }
    if proxy:
        agent_kwargs["browser"] = browser_use.Browser(
            proxy=browser_use.browser.ProxySettings(server=proxy)
        )

    return browser_use.Agent(**agent_kwargs)


async def run_one_task(task: TaskRecord) -> None:
    agent = _build_agent(task)
    history = await agent.run()
    save_run_record(serialize_run(task.id, task.prompt, history))
