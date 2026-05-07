from __future__ import annotations

import pydantic


class PromptImprovement(pydantic.BaseModel):
    original_prompt: str
    improved_prompt: str
    reason: str
    changes: list[str] = pydantic.Field(default_factory=list)


class HintImprovement(pydantic.BaseModel):
    new_hints: list[str] = pydantic.Field(default_factory=list)
    step_guidance: dict[int, str] = pydantic.Field(default_factory=dict)
    reason: str


class UIRecommendation(pydantic.BaseModel):
    element_id: str = ""
    element_selector: str = ""
    recommendation: str
    priority: str = "medium"  # low, medium, high
    impact: str = ""


class ImprovementPlan(pydantic.BaseModel):
    task_id: int | str
    analysis_run_id: str
    failure_type: str | None = None
    prompt_improvement: PromptImprovement | None = None
    hint_improvement: HintImprovement | None = None
    ui_recommendations: list[UIRecommendation] = pydantic.Field(default_factory=list)
    overall_strategy: str = ""
    confidence: float = 0.0
