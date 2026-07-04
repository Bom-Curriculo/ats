from pydantic import BaseModel, ConfigDict, Field



class AIJobClassification(BaseModel):
    title: str | None = None
    seniority: str | None = None
    area: str | None = None
    core_requirements: list[str] = Field(default_factory=list)
    secondary_requirements: list[str] = Field(default_factory=list)
    differentials: list[str] = Field(default_factory=list)


    # Implementation note.
    hard_filters: list[str] = Field(default_factory=list)
    business_context: list[str] = Field(default_factory=list)
    confidence: int | None = Field(default=None, ge=0, le=100)
    company: str | None = None
    technologies: list[str] = Field(default_factory=list)


    responsibilities: list[str] = Field(default_factory=list)


    modality: str | None = None
    location: str | None = None


    # Technical note removed during English standardization.
    accepts_no_experience: bool = False


    # Ignore extra provider fields.
    model_config = ConfigDict(extra="ignore")



class SelectedEvidence(BaseModel):
    item: str
    source: str | None = None


    source_type: str | None = None
    excerpt: str | None = None


    # Technical note removed during English standardization.
    evidence_level: str = "no_evidence"
    confidence: int | None = Field(default=None, ge=0, le=100)
    related_to: list[str] = Field(default_factory=list)



class ContextualRequirementEvaluation(BaseModel):
    item: str
    importance: str = "not_provided"
    job_relevance: str = "medium"
    status: str = "not_evaluated"
    used_evidence: SelectedEvidence | None = None

    # Implementation note.
    real_gap: bool = False

    # Technical note removed during English standardization.
    description_gap: bool = False
    recommendation_safe: str = ""
    # Implementation note.
    hallucination_risk: str = "low"
    model_config = ConfigDict(extra="ignore")



class AIPipelineResult(BaseModel):
    job_classification: AIJobClassification | None = None
    relevant_evidence: list[SelectedEvidence] = Field(default_factory=list)
    requirement_evaluations: list[ContextualRequirementEvaluation] = Field(default_factory=list)
    prioritized_gaps: list[dict] = Field(default_factory=list)


    safe_suggestions: list[str] = Field(default_factory=list)
    contextual_ai_score: int | None = Field(default=None, ge=0, le=100)
    pipeline_confidence: int | None = Field(default=None, ge=0, le=100)


    # Implementation note.
    executed_steps: list[str] = Field(default_factory=list)


    # Implementation note.
    fallback_steps: list[str] = Field(default_factory=list)


    fallback_details: list[dict] = Field(default_factory=list)
