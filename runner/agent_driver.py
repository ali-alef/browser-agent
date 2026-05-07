from __future__ import annotations

import browser_use

from runner import models as runner_models
from runner import serializer as runner_serializer
from tasks import models as task_models
from storage import registry as storage_registry
import settings


async def run_one_task(task: task_models.TaskRecord) -> runner_models.Run:
    """Run a task with the AI agent, optionally with hints injected."""
    
    # Enrich task prompt with hints if available
    enriched_prompt = _enrich_prompt_with_hints(task)
    
    agent_kwargs = {
        "task": enriched_prompt.strip(),
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


def _enrich_prompt_with_hints(task: task_models.TaskRecord) -> str:
    """Enrich the task prompt with hints and guidance if available."""
    
    if not task.hints and not task.step_guidance:
        return task.prompt
    
    enriched = task.prompt
    
    if task.hints:
        hints_text = "\n".join([f"- {hint}" for hint in task.hints])
        enriched += f"\n\n[HELPFUL HINTS]\n{hints_text}"
    
    if task.step_guidance:
        step_guidance_text = "\n".join(
            [f"Step {step}: {guidance}" for step, guidance in sorted(task.step_guidance.items())]
        )
        enriched += f"\n\n[STEP-BY-STEP GUIDANCE]\n{step_guidance_text}"
    
    return enriched
