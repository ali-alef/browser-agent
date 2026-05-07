import pydantic


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


class LLMJudgeOutput(pydantic.BaseModel):
    status: str
    verdict_reason: str
    failure_type: str | None = None
    failure_step: int | str | None = None
    expected_action: str = ""
    expected_strategy: str = ""
    confidence: float = 0.0
    evidence: list[str] = pydantic.Field(default_factory=list)
    improvement_hint: str = ""
    weaknesses: list[str] = pydantic.Field(default_factory=list)
    key_findings: list[str] = pydantic.Field(default_factory=list)
    step_assessments: list[StepAssessment] = pydantic.Field(default_factory=list)
