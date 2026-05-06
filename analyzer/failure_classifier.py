from __future__ import annotations

import json
import os
import re
from typing import Any

import pydantic

from chatgpt_api import ChatCompletionRequest, chat_completion
from runner.model import Run, Step


class FailureReport(pydantic.BaseModel):
    failure_type: str
    failure_step: int | None = None
    expected_action: str = ""
    expected_strategy: str = ""
    confidence: float = 0.0
    evidence: list[str] = pydantic.Field(default_factory=list)
    improvement_hint: str = ""


class StepAssessment(pydantic.BaseModel):
    step_number: int
    actions: list[str] = pydantic.Field(default_factory=list)
    necessary: bool = True
    progress_made: bool = False
    correct: bool = False
    reason: str = ""


class RunAnalysis(pydantic.BaseModel):
    run_id: str
    task_id: str | int
    task_prompt: str = ""
    status: str
    verdict_reason: str
    failure_report: FailureReport | None = None
    step_assessments: list[StepAssessment] = pydantic.Field(default_factory=list)
    unnecessary_steps: list[int] = pydantic.Field(default_factory=list)
    weaknesses: list[str] = pydantic.Field(default_factory=list)
    key_findings: list[str] = pydantic.Field(default_factory=list)
    llm_model: str = ""


class _LLMJudgeOutput(pydantic.BaseModel):
    status: str
    verdict_reason: str
    failure_type: str | None = None
    failure_step: int | None = None
    expected_action: str = ""
    expected_strategy: str = ""
    confidence: float = 0.0
    evidence: list[str] = pydantic.Field(default_factory=list)
    improvement_hint: str = ""
    weaknesses: list[str] = pydantic.Field(default_factory=list)
    key_findings: list[str] = pydantic.Field(default_factory=list)
    step_assessments: list[StepAssessment] = pydantic.Field(default_factory=list)


def analyze_run_log(run_record: Run) -> RunAnalysis:
    llm_output = _judge_with_llm(run=run_record)

    unnecessary_steps = [item.step_number for item in llm_output.step_assessments if not item.necessary]
    failure_report = None
    if llm_output.status == "failure":
        failure_report = FailureReport(
            failure_type=llm_output.failure_type or "ambiguous",
            failure_step=llm_output.failure_step,
            expected_action=llm_output.expected_action,
            expected_strategy=llm_output.expected_strategy,
            confidence=max(0.0, min(1.0, llm_output.confidence)),
            evidence=llm_output.evidence[:8],
            improvement_hint=llm_output.improvement_hint,
        )

    return RunAnalysis(
        run_id=run_record.run_id,
        task_id=run_record.task_id,
        task_prompt=run_record.task_prompt.strip(),
        status=llm_output.status,
        verdict_reason=llm_output.verdict_reason,
        failure_report=failure_report,
        step_assessments=llm_output.step_assessments,
        unnecessary_steps=unnecessary_steps,
        weaknesses=llm_output.weaknesses,
        key_findings=llm_output.key_findings,
    )


def _judge_with_llm(run: Run) -> _LLMJudgeOutput:
    system_prompt = (
        "You are a QA evaluator for browser-agent run logs. "
        "Judge whether the task was achieved from the provided trace, classify root cause if failed, "
        "and assess necessity of each step. "
        "Return strict JSON only."
    )
    user_prompt = _build_judge_prompt(run)

    response_text = chat_completion(
        request_data=ChatCompletionRequest(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        ),
    ).content
    raw_json = _extract_json_object(response_text)
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Analyzer LLM returned non-JSON response: {exc}") from exc

    return _LLMJudgeOutput.model_validate(parsed)


def _serialize_step_for_llm(step: Step) -> dict[str, Any]:
    actions = [{"type": action.type, **action.metadata} for action in step.actions]
    results = [
        {
            "error": result.error,
            "content": result.content,
        }
        for result in step.results
    ]

    return {
        "step_number": step.step_number,
        "actions": actions,
        "results": results,
        "previous_goal": step.previous_goal,
        "next_goal": step.next_goal,
        "memory": step.memory,
        "thinking": step.thinking,
        "page_stats": _extract_tag_content(step.ai_input_message, "page_stats"),
        "page_info": _extract_tag_content(step.ai_input_message, "page_info"),
        "current_tab": _extract_current_tab(step.ai_input_message),
        "interactive_elements": _extract_interactive_elements_text(step.ai_input_message),
    }


def _build_judge_prompt(run: Run) -> str:
    steps = [_serialize_step_for_llm(step) for step in run.steps]
    trace_context = {
        "task_prompt": run.task_prompt.strip(),
        "run_metadata": {
            "run_id": run.run_id,
            "task_id": run.task_id,
            "agent_version": run.agent_version,
            "final_status": run.final_status,
            "final_output": run.final_output,
            "judgment": run.judgment,
            "steps_count": len(run.steps),
        },
        "steps": steps,
    }

    schema = {
        "status": "success|failure|unknown",
        "verdict_reason": "short but concrete explanation",
        "failure_type": (
            "navigation_failure|element_not_found|wrong_element_interaction|"
            "extraction_error|hallucination|loop_or_stuck|timeout|environment|ambiguous|null"
        ),
        "failure_step": "int|null",
        "expected_action": "string",
        "expected_strategy": "string",
        "confidence": "0.0-1.0",
        "evidence": ["string"],
        "improvement_hint": "string",
        "weaknesses": ["string"],
        "key_findings": ["string"],
        "step_assessments": [
            {
                "step_number": "int",
                "actions": ["string"],
                "necessary": "boolean",
                "progress_made": "boolean",
                "correct": "boolean",
                "reason": "string",
            }
        ],
    }

    return (
        "Role: You are a forensic evaluator for one browser-agent task run.\n"
        "Goal: Reconstruct the agent's decision process and identify where behavior diverged from the correct strategy.\n\n"
        "Hard rules:\n"
        "1) Base reasoning only on provided trace context.\n"
        "2) Do not assume hidden/missing steps.\n"
        "3) Do NOT rely on run_metadata.judgment; independently verify from steps + final_output.\n"
        "4) Treat browser_state-derived fields (interactive_elements, observable_hints, page_info, page_stats) as ground truth over agent thinking/memory when they conflict.\n"
        "5) A run can still be SUCCESS even with inefficient/redundant actions; do not mark failure only because some steps were unnecessary.\n"
        "6) Mark a step as necessary=false when the needed control/element is already visible and usable before that action.\n"
        "7) For scroll actions: if search/product/price-relevant controls were already visible in the same step context, score the scroll as unnecessary.\n"
        "8) If final_output is supported by trace evidence (navigation/search/open first product/extract price), prefer success even if route was suboptimal.\n"
        "9) If final_output looks correct but trace does not support the required actions/extraction, classify failure_type='hallucination'.\n"
        "10) Prefer earliest root-cause failure over later symptoms and set failure_step to that earliest divergence.\n"
        "11) If evidence is insufficient, use status='unknown' and failure_type='ambiguous'.\n"
        "12) For failures, expected_action and expected_strategy must describe what should have happened at failure_step.\n"
        "13) improvement_hint must be specific, implementable, and reference observed trace behavior.\n"
        "14) Justify conclusions with concrete trace evidence.\n"
        "15) Evaluate only this one task, one trace, one decision outcome.\n\n"
        "Failure taxonomy:\n"
        "- navigation_failure: wrong URL/page path or failed navigation flow.\n"
        "- element_not_found: required UI element was not located/accessed.\n"
        "- wrong_element_interaction: interacted with incorrect element or wrong action on element.\n"
        "- extraction_error: reached target context but extracted wrong/missing value.\n"
        "- hallucination: claimed result without supporting trace evidence.\n"
        "- loop_or_stuck: repetitive/non-progressing behavior.\n"
        "- timeout: run ended due to time limits before completion.\n"
        "- environment: external blockers (network/auth/captcha/service outage).\n"
        "- ambiguous: insufficient evidence.\n\n"
        "Step assessment definitions:\n"
        "- necessary: contributes to task completion and was not already available from visible UI state.\n"
        "- progress_made: moved closer to goal.\n"
        "- correct: action appropriate for observed state.\n\n"
        "Causal reasoning requirement:\n"
        "Explain as chain: what agent saw -> what it did -> why it was wrong/right -> what should have been done.\n\n"
        "Output must be strict JSON matching schema exactly.\n\n"
        f"Output schema:\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n\n"
        f"Trace context:\n{json.dumps(trace_context, indent=2, ensure_ascii=False)}\n"
    )


def _extract_tag_content(message: str | None, tag: str) -> str:
    if not message:
        return ""
    match = re.search(fr"<{tag}>(.*?)</{tag}>", message, flags=re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_current_tab(message: str | None) -> str:
    if not message:
        return ""
    match = re.search(r"^\s*Current tab:\s*(.+)$", message, flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_interactive_elements_text(message: str | None) -> str:
    if not message:
        return ""
    start_marker = "Interactive elements:"
    start_idx = message.find(start_marker)
    if start_idx == -1:
        return ""
    tail = message[start_idx + len(start_marker) :]
    for end_marker in ("\nCurrent screenshot:", "\n</browser_state>"):
        end_idx = tail.find(end_marker)
        if end_idx != -1:
            tail = tail[:end_idx]
            break
    return tail.strip()


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    if "```json" in stripped:
        start = stripped.find("```json")
        end = stripped.find("```", start + 7)
        if end != -1:
            candidate = stripped[start + 7 : end].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate

    first = stripped.find("{")
    last = stripped.rfind("}")
    if first != -1 and last != -1 and last > first:
        return stripped[first : last + 1]
    raise RuntimeError("No JSON object found in analyzer LLM response.")


def analyze(run_record: Run) -> None:
    run_analyze = analyze_run_log(run_record)
    json.dump(
        run_analyze.model_dump(mode="json", serialize_as_any=True),
        open(f"storage/analys/analys_{run_analyze.task_id}_{run_analyze.run_id}.json", mode='w'),
        indent=2,
        ensure_ascii=False,
    )
