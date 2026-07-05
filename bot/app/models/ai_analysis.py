from typing import Literal


from pydantic import BaseModel, ConfigDict, Field



# Restrict status values to the supported contract.
AIRequirementStatus = Literal[
    "found_with_evidence",
    "found_without_clear_context",

    "related_but_not_explicit",

    "missing",
    "not_evaluated",
    "possible_blocker",

]



AIRequirementImportance = Literal[
    "required", "desired", "differential", "contextual", "not_provided"
]



AIRequirementCategory = Literal[
    "technical_skill",
    "tool",
    "experience",
    "education",
    "language",


    "soft_skill",
    "business_domain",
    "certification",
    "availability",
    "location",
    "other",


]



class AIRequirementAnalysis(BaseModel):
    item: str = Field(min_length=1)
    category: AIRequirementCategory
    importance: AIRequirementImportance
    status: AIRequirementStatus


    evidence: str | None = None
    rationale: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    # Reject unknown fields to keep provider output strict.
    model_config = ConfigDict(extra="forbid")



class AIAnalysisResponse(BaseModel):
    contextual_summary: str = Field(min_length=1)
    contextual_requirements: list[AIRequirementAnalysis]
    strengths: list[str]
    gaps: list[str]
    possible_blockers: list[str]
    improvement_suggestions: list[str]
    next_steps: list[str]

    # Implementation note.
    anti_fabrication_alerts: list[str]

    confidence: int = Field(ge=0, le=100)
    ai_suggested_score: int | None = Field(default=None, ge=0, le=100)
    ai_score_rationale: str | None = None

    ai_roles: list[str] = Field(default_factory=list)


    ai_context_quality: int | None = Field(default=None, ge=0, le=100)


    relevance_evaluation: dict | None = None


    evidence_matrix: list[dict] = Field(default_factory=list)


    prioritized_gaps: list[dict] = Field(default_factory=list)
    safe_rewrite_suggestions: list[str] = Field(default_factory=list)
    ats_diagnostics: dict | None = None
    contextual_ai_score: int | None = Field(default=None, ge=0, le=100)


    model_config = ConfigDict(extra="forbid")
