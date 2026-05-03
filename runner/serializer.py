from __future__ import annotations

from typing import Any
from uuid import uuid4

from browser_use.agent.views import AgentHistoryList, AgentStructuredOutput

from runner.model import Step, Action, Result, Run


def serialize_run(task_id: int, task_prompt: str, history: AgentHistoryList[AgentStructuredOutput]) -> Run:
    payload = history.model_dump()
    raw_steps = payload.get("history")

    return Run(
        run_id=str(uuid4()),
        task_id=task_id,
        task_prompt=task_prompt,
        agent_version="gemini-2.5-flash",
        steps=serialize_steps(raw_steps),
        judgment=_extract_judgment(raw_steps),
        final_output=history.final_result() or "",
        final_status="completed" if history.is_successful() and history.is_done() else "failed",
    )


def serialize_steps(raw_history: list[dict[str, Any]]) -> list[Step]:
    serialized_steps: list[Step] = []
    for i, raw_step in enumerate(raw_history, start=1):
        model_output = raw_step.get("model_output") or {}

        step = Step(
            step_number=i,
            actions=_extract_actions(model_output),
            results=_extract_results(raw_step),
            ai_input_message=raw_step.get("state_message"),
            next_goal=model_output.get("next_goal", ""),
            previous_goal=model_output.get("evaluation_previous_goal", ""),
            memory=model_output.get("memory", ""),
            thinking=model_output.get("thinking", ""),
        )
        serialized_steps.append(step)
    return serialized_steps


def _extract_actions(model_output: dict[str, Any]) -> list[Action]:
    actions = model_output.get("action") or []
    action_items: list[Action] = []
    for action in actions:
        if not isinstance(action, dict) or not action:
            continue
        action_type = str(next(iter(action.keys())))
        metadata = action.get(action_type)
        action_items.append(
            Action(
                type=action_type,
                metadata=metadata if isinstance(metadata, dict) else {},
            )
        )
    return action_items


def _extract_results(raw_step: dict[str, Any]) -> list[Result]:
    result_items: list[Result] = []
    for result in raw_step.get("result") or []:
        if not isinstance(result, dict):
            continue
        error = result.get("error")
        content = result.get("extracted_content")
        result_items.append(
            Result(
                error=str(error) if error is not None else None,
                content=str(content) if content is not None else None,
            )
        )
    return result_items


def _extract_judgment(raw_steps: list[dict[str, Any]]) -> str:
    if not raw_steps:
        return ""
    last_results = raw_steps[-1].get("result") or []
    if not last_results:
        return ""
    last_result = last_results[0] or {}
    judgment = last_result.get("judgement") or {}
    reasoning = judgment.get("reasoning")
    return str(reasoning) if reasoning is not None else ""
