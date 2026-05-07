from __future__ import annotations

import browser_use

from runner import models as runner_models
from runner import serializer as runner_serializer
from tasks import models as task_models
from storage import registry as storage_registry
from improver import models as improver_models
import settings


async def run_one_task(task: task_models.TaskRecord, improvement: improver_models.ImprovementPlan) -> runner_models.Run:
    if improvement:
        task = _apply_improvement_to_task(task, improvement)
    
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


def _apply_improvement_to_task(task: task_models.TaskRecord, improvement) -> task_models.TaskRecord:
    updated_task = task.model_copy()
    
    if improvement.prompt_improvement:
        updated_task.prompt = improvement.prompt_improvement.improved_prompt
    
    if improvement.hint_improvement:
        updated_task.hints = improvement.hint_improvement.new_hints
        if improvement.hint_improvement.step_guidance:
            updated_task.step_guidance = improvement.hint_improvement.step_guidance
    
    return updated_task


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
