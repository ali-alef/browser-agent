from __future__ import annotations

import json

from analyzer import models as analyzer_models
from chatgpt_api import models as chatgpt_models, client as chatgpt_client
from improver import models as improver_models
from storage import registry as storage_registry
from utils import extract_json_object


def generate_improvement_plan(analysis: analyzer_models.RunAnalysis) -> None:
    improvement_suggestions = _get_improvement_suggestions(analysis)
    
    improvement = improver_models.ImprovementPlan(
        task_id=analysis.task_id,
        analysis_run_id=analysis.run_id,
        failure_type=analysis.failure_report.failure_type if analysis.failure_report else None,
        prompt_improvement=improvement_suggestions.get("prompt"),
        hint_improvement=improvement_suggestions.get("hints"),
        ui_recommendations=improvement_suggestions.get("ui_recommendations", []),
        overall_strategy=improvement_suggestions.get("strategy", ""),
        confidence=analysis.failure_report.confidence if analysis.failure_report else 0.0,
    )

    storage_registry.save_improvement_plan(improvement)


def _get_improvement_suggestions(analysis: analyzer_models.RunAnalysis) -> dict:
    system_prompt = (
        "You are an expert at improving AI agent task prompts and providing strategic hints. "
        "Based on task failure analysis, generate specific, actionable improvements. "
        "Return strict JSON only."
    )
    
    user_prompt = _build_improvement_prompt(analysis)
    
    response_text = chatgpt_client.chat_completion(
        request_data=chatgpt_models.ChatCompletionRequest(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        ),
    ).content
    
    raw_json = extract_json_object(response_text)
    try:
        suggestions = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Improver LLM returned non-JSON response: {exc}") from exc
    
    improvements = {}
    
    # Process prompt improvement
    if suggestions.get("improved_prompt"):
        improvements["prompt"] = improver_models.PromptImprovement(
            original_prompt=analysis.task_prompt,
            improved_prompt=suggestions["improved_prompt"],
            reason=suggestions.get("prompt_improvement_reason", ""),
            changes=suggestions.get("prompt_changes", []),
        )
    
    # Process hint improvements
    if suggestions.get("new_hints") or suggestions.get("step_guidance"):
        improvements["hints"] = improver_models.HintImprovement(
            new_hints=suggestions.get("new_hints", []),
            step_guidance=suggestions.get("step_guidance", {}),
            reason=suggestions.get("hints_reason", ""),
        )
    
    # Process UI recommendations
    ui_recs = []
    for rec in suggestions.get("ui_recommendations", []):
        ui_recs.append(improver_models.UIRecommendation(
            element_id=rec.get("element_id", ""),
            element_selector=rec.get("element_selector", ""),
            recommendation=rec.get("recommendation", ""),
            priority=rec.get("priority", "medium"),
            impact=rec.get("impact", ""),
        ))
    if ui_recs:
        improvements["ui_recommendations"] = ui_recs
    
    improvements["strategy"] = suggestions.get("overall_strategy", "")
    
    return improvements


def _build_improvement_prompt(analysis: analyzer_models.RunAnalysis) -> str:
    failure_context = ""
    if analysis.failure_report:
        failure_context = f"""
        Failure Analysis:
            - Type: {analysis.failure_report.failure_type}
            - Step: {analysis.failure_report.failure_step}
            - Expected Action: {analysis.failure_report.expected_action}
            - Expected Strategy: {analysis.failure_report.expected_strategy}
            - Evidence: {analysis.failure_report.evidence}
            - Improvement Hint from Analyzer: {analysis.failure_report.improvement_hint}
            - Confidence: {analysis.failure_report.confidence}
        """
    
    schema = {
        "improved_prompt": "string - refined task prompt that is clearer and more precise",
        "prompt_improvement_reason": "string - why this prompt is better",
        "prompt_changes": ["string - list of specific changes made"],
        "new_hints": ["string - step-by-step hints to guide the agent"],
        "step_guidance": {
            "1": "string - guidance for step 1",
            "2": "string - guidance for step 2",
        },
        "hints_reason": "string - why these hints help",
        "ui_recommendations": [
            {
                "element_id": "string - identifier of UI element",
                "element_selector": "string - CSS selector or XPath",
                "recommendation": "string - what should be improved",
                "priority": "high|medium|low",
                "impact": "string - how this helps the agent",
            }
        ],
        "overall_strategy": "string - high-level strategy for improvement",
    }
    
    weaknesses = "\n".join([f"- {w}" for w in analysis.weaknesses])
    findings = "\n".join([f"- {f}" for f in analysis.key_findings])
    
    return f"""You are analyzing a failed AI agent task run and must generate improvements.

Original Task: {analysis.task_prompt}

{failure_context}

Weaknesses Identified:
{weaknesses}

Key Findings:
{findings}

Your task is to generate specific improvements that will help the agent succeed:

1. **Improved Prompt**: Clarify ambiguous language, add missing context, break down complex steps.
2. **Hints**: Provide step-by-step guidance for critical decision points.
3. **Step Guidance**: For critical steps, provide explicit expected behavior.
4. **UI Recommendations**: Suggest improvements to make UI elements clearer/more discoverable.
5. **Overall Strategy**: Explain the improvement philosophy.

Output must be valid JSON matching this schema exactly:
{json.dumps(schema, indent=2)}

Focus on making improvements that are:
- Specific and actionable
- Based on the failure analysis
- Implementable without modifying the target website
- Clear enough for an AI agent to understand
"""
