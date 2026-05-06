from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Literal

import pydantic

from runner.model import Run, Step


DEFAULT_ANALYZER_MODEL = "gpt-4o"
DEFAULT_API_BASE = "http://34.72.104.120/"


class FailureReport(pydantic.BaseModel):
    failure_type: str
    confidence: float = 0.0
    evidence: list[str] = pydantic.Field(default_factory=list)
    suggested_fix_area: str = ""


class StepAssessment(pydantic.BaseModel):
    step_number: int
    actions: list[str] = pydantic.Field(default_factory=list)
    necessary: bool = True
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
    confidence: float = 0.0
    evidence: list[str] = pydantic.Field(default_factory=list)
    suggested_fix_area: str = ""
    weaknesses: list[str] = pydantic.Field(default_factory=list)
    key_findings: list[str] = pydantic.Field(default_factory=list)
    step_assessments: list[StepAssessment] = pydantic.Field(default_factory=list)


def analyze_run_log(run_record: Run) -> RunAnalysis:
    analyzer_model = os.getenv("ANALYZER_MODEL", DEFAULT_ANALYZER_MODEL)

    llm_output = _judge_with_llm(
        run=run_record,
        api_key="sk-tRFUVokeNnPpOsjoU0zlDw",
        model=analyzer_model,
        api_base=os.getenv("OPENAI_API_BASE", DEFAULT_API_BASE),
        timeout_seconds=10,
    )

    unnecessary_steps = [item.step_number for item in llm_output.step_assessments if not item.necessary]
    failure_report = None
    if llm_output.status == "failure":
        failure_report = FailureReport(
            failure_type=llm_output.failure_type or "ambiguous",
            confidence=max(0.0, min(1.0, llm_output.confidence)),
            evidence=llm_output.evidence[:8],
            suggested_fix_area=llm_output.suggested_fix_area,
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
        llm_model=analyzer_model,
    )


def _judge_with_llm(
    run: Run,
    api_key: str | None,
    model: str,
    api_base: str,
    timeout_seconds: int,
) -> _LLMJudgeOutput:
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for analyzer LLM judgment.")

    system_prompt = (
        "You are a QA evaluator for browser-agent run logs. "
        "Judge whether the task was achieved from the provided trace, classify root cause if failed, "
        "and assess necessity of each step. "
        "Return strict JSON only."
    )
    user_prompt = _build_judge_prompt(run)

    response_text = _chat_completion(
        api_key=api_key,
        api_base=api_base,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        timeout_seconds=timeout_seconds,
    )
    raw_json = _extract_json_object(response_text)
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Analyzer LLM returned non-JSON response: {exc}") from exc

    return _LLMJudgeOutput.model_validate(parsed)


def _build_judge_prompt(run: Run) -> str:
    steps = [_serialize_step_for_llm(step) for step in run.steps]
    trace_context = {
        "task_prompt": run.task_prompt.strip(),
        "run_metadata": {
            "run_id": run.run_id,
            "task_id": run.task_id,
            "agent_version": run.agent_version,
            "final_status": run.final_status,
            "final_output": _trim(run.final_output, 1200),
            "judgment": _trim(run.judgment, 800),
            "steps_count": len(run.steps),
        },
        "steps": steps,
    }

    schema = {
        "status": "success|failure|uncertain",
        "verdict_reason": "short but concrete explanation",
        "failure_type": "site_ui|agent_reasoning|environment|ambiguous|null",
        "confidence": "0.0-1.0",
        "evidence": ["string"],
        "suggested_fix_area": "string",
        "weaknesses": ["string"],
        "key_findings": ["string"],
        "step_assessments": [
            {
                "step_number": "int",
                "actions": ["string"],
                "necessary": "boolean",
                "reason": "string",
            }
        ],
    }

    return (
        "Evaluate this run.\n\n"
        "Rules:\n"
        "1) Determine if the task is actually completed using task prompt + trace evidence.\n"
        "2) If failed, classify failure_type:\n"
        "   - site_ui: bad selectors, popups, hidden/unreachable elements, DOM/readability issues.\n"
        "   - agent_reasoning: wrong decisions, loops, misinterpretation, poor planning.\n"
        "   - environment: network/auth/captcha/infra/external service issues.\n"
        "   - ambiguous: insufficient evidence.\n"
        "3) Assess each step necessity relative to goal progress.\n"
        "4) Include weaknesses even when status is success.\n"
        "5) Output must be valid JSON only and follow the schema exactly.\n\n"
        f"Output schema:\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n\n"
        f"Trace context:\n{json.dumps(trace_context, indent=2, ensure_ascii=False)}\n"
    )


def _serialize_step_for_llm(step: Step) -> dict[str, Any]:
    actions = [{"type": action.type, "metadata": _compact_metadata(action.metadata)} for action in step.actions]
    results = [
        {
            "error": _trim(result.error, 400),
            "content": _trim(result.content, 500),
        }
        for result in step.results
    ]
    return {
        "step_number": step.step_number,
        "actions": actions,
        "results": results,
        "previous_goal": _trim(step.previous_goal, 350),
        "next_goal": _trim(step.next_goal, 350),
        "memory": _trim(step.memory, 350),
        "thinking": _trim(step.thinking, 500),
        "ai_input_excerpt": _trim(step.ai_input_message, 900),
    }


def _compact_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if not metadata:
        return {}
    keep_keys = (
        "index",
        "url",
        "text",
        "keys",
        "seconds",
        "new_tab",
        "down",
        "pages",
        "query",
        "engine",
    )
    compact: dict[str, Any] = {}
    for key in keep_keys:
        if key in metadata:
            compact[key] = _trim_value(metadata[key], 200)
    return compact


def _trim_value(value: Any, max_len: int) -> Any:
    if isinstance(value, str):
        return _trim(value, max_len)
    if isinstance(value, list):
        return [_trim_value(item, max_len) for item in value[:10]]
    if isinstance(value, dict):
        return {k: _trim_value(v, max_len) for k, v in list(value.items())[:15]}
    return value


def _trim(text: str | None, max_len: int) -> str | None:
    if text is None:
        return None
    clean = text.strip()
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 3] + "..."


def _chat_completion(
    *,
    api_key: str,
    api_base: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int,
) -> str:
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    parsed = json.loads(body)
    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI response shape: {body[:500]}") from exc


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

