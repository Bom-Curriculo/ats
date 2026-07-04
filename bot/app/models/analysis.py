from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.models.ai_pipeline import (
    ContextualRequirementEvaluation,
    AIJobClassification,
    SelectedEvidence,
    AIPipelineResult,
)


ResumeSourceType = Literal[
    "resume_text", "resume_pdf", "linkedin_pdf", "linkedin_text", "linkedin_url",
    "github_url", "portfolio_url", "portfolio_text", "job_text", "job_url",
    "personal_information", "custom_instructions",
    # Legacy public API compatibility.
    "curriculo_texto", "curriculo_pdf", "vaga_texto", "vaga_url",
    "informacoes_pessoais", "instrucoes_customizadas",
]


class ResumeSource(BaseModel):
    type: ResumeSourceType
    content: str | None = None
    url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data):
        if not isinstance(data, dict):
            return data
        mapped = dict(data)
        if "type" not in mapped and "tipo" in mapped:
            mapped["type"] = mapped["tipo"]
        if "content" not in mapped and "conteudo" in mapped:
            mapped["content"] = mapped["conteudo"]
        return mapped


class AnalysisRequest(BaseModel):
    resume_text: str = Field(
        default="",
        description="Full resume text",
    )

    job_text: str = Field(
        min_length=1,
        description="Full job description",
    )

    language: str = Field(
        default="pt-BR",
        min_length=2,
    )

    # Implementation note.
    use_ai: bool | None = Field(
        default=None,
    )

    job_level: str | None = Field(
        default=None,
    )
    resume_sources: list[ResumeSource] = Field(
        default_factory=list,
    )

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, data):
        if not isinstance(data, dict):
            return data
        mapped = dict(data)
        legacy_fields = {
            "curriculo_texto": "resume_text",
            "vaga_texto": "job_text",
            "idioma": "language",
            "usar_ia": "use_ai",
            "nivel_vaga": "job_level",
            "fontes_curriculo": "resume_sources",
        }
        for legacy_name, field_name in legacy_fields.items():
            if field_name not in mapped and legacy_name in mapped:
                mapped[field_name] = mapped[legacy_name]
        return mapped

    @model_validator(mode="after")
    def consolidate_text_sources(self):
        if not self.resume_text.strip():
            text_source_types = {"resume_text", "linkedin_text", "portfolio_text", "personal_information", "custom_instructions", "curriculo_texto", "informacoes_pessoais", "instrucoes_customizadas"}
            texts = [source.content.strip() for source in self.resume_sources
                     if source.type in text_source_types and source.content and source.content.strip()]
            if not texts:
                raise ValueError("resume_text or a textual resume source is required")
            self.resume_text = "\n\n".join(texts)
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resume_text": "resume text",
                "job_text": "job description",
                "language": "en-US",
            }
        }
    )


class PrivacyInformation(BaseModel):
    """Safe metadata describing preprocessing before an AI call."""

    sensitive_data_detected: bool = False

    items_removed_before_ai: list[str] = Field(default_factory=list)

    ai_text_was_sanitized: bool = False


class DetailedAnalysis(BaseModel):
    """Detailed classification of job matches."""

    found_required_requirements: list[str] = Field(default_factory=list)

    missing_required_requirements: list[str] = Field(default_factory=list)

    found_differentials: list[str] = Field(default_factory=list)

    missing_differentials: list[str] = Field(default_factory=list)

    found_technologies: list[str] = Field(default_factory=list)

    missing_technologies: list[str] = Field(default_factory=list)

    possible_blockers: list[str] = Field(default_factory=list)


class DetailedSuggestions(BaseModel):
    """Suggestions separated without assuming experience."""

    recommended_adjustments: list[str] = Field(default_factory=list)

    technical_gaps: list[str] = Field(default_factory=list)

    attention_points: list[str] = Field(default_factory=list)

    next_steps: list[str] = Field(default_factory=list)

    resume_adjustments: list[str] = Field(default_factory=list)
    real_gaps: list[str] = Field(default_factory=list)
    study_next_steps: list[str] = Field(default_factory=list)
    anti_fabrication_alerts: list[str] = Field(default_factory=list)


class RequirementAnalysisItem(BaseModel):
    """Analysis and guidance for one job requirement."""

    item: str

    type: str

    category: str

    weight: int

    status: str

    resume_evidence: str | None = None

    guidance: str

    evidence_level: str = "no_evidence"

    evidence_source: str | None = None

    inference_strength: str | None = None


class ResumeEvidence(BaseModel):
    professional_experience: bool = False

    personal_projects: bool = False

    academic_projects: bool = False

    open_source: bool = False

    courses: bool = False

    technology_residency: bool = False

    skills_section: bool = False


class AIFallback(BaseModel):
    """Sanitized provider-attempt metadata."""

    fallback_used: bool = False

    attempted_providers: list[str] = Field(default_factory=list)

    providers_skipped_by_configuration: list[str] = Field(default_factory=list)

    last_sanitized_error: str | None = None

    sanitized_provider_errors: list[str] = Field(default_factory=list)


class SanitizedProviderError(BaseModel):
    provider: str
    model: str | None = None
    error_category: str
    status_http: int | None = None
    safe_message: str


class ItemKeyword(BaseModel):
    term: str
    category: str
    weight: float
    present: bool
    source: str | None = None


class KeywordReport(BaseModel):
    hard_skills: list[ItemKeyword] = Field(default_factory=list)
    title_function_keywords: list[ItemKeyword] = Field(default_factory=list)
    business_context: list[ItemKeyword] = Field(default_factory=list)
    action_keywords: list[ItemKeyword] = Field(default_factory=list)
    domain_keywords: list[ItemKeyword] = Field(default_factory=list)
    hard_filters: list[ItemKeyword] = Field(default_factory=list)
    hard_filter_alerts: list[str] = Field(default_factory=list)


class FactBank(BaseModel):
    experiences: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    courses: list[dict] = Field(default_factory=list)
    skills: list[dict] = Field(default_factory=list)
    languages: list[dict] = Field(default_factory=list)
    academic_projects: list[dict] = Field(default_factory=list)
    freelance: list[dict] = Field(default_factory=list)
    open_source: list[dict] = Field(default_factory=list)
    residencies: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    achievements: list[dict] = Field(default_factory=list)
    technologies_by_source: dict[str, list[str]] = Field(default_factory=dict)
    evidence_items: list[dict] = Field(default_factory=list)


class RequirementGroup(BaseModel):
    name: str
    type: str
    mode: str
    items: list[str] = Field(default_factory=list)
    group_status: str
    summarized_evidence: str | None = None
    score_impact: float = 0
    rationale: str | None = None


class AnalysisResult(BaseModel):
    """Complete internal analysis result."""

    ats_score: int = Field(ge=0, le=100, serialization_alias="pontuacao_ats")

    matched_keywords: list[str] = Field(serialization_alias="palavras_chave_encontradas")

    missing_keywords: list[str] = Field(serialization_alias="palavras_chave_faltando")

    detected_issues: list[str] = Field(serialization_alias="problemas_detectados")

    suggestions: list[str]

    generated_summary: str = Field(serialization_alias="resumo_gerado")

    ai_provider: str = Field(default="sem_ia", serialization_alias="provedor_ia")

    ai_model: str | None = Field(default=None, serialization_alias="modelo_ia")

    privacy: PrivacyInformation | None = None

    detailed_analysis: DetailedAnalysis | None = None

    detailed_suggestions: DetailedSuggestions | None = None

    valid_analysis: bool = True

    input_alerts: list[str] = Field(default_factory=list)

    resume_inventory: dict[str, list[str]] | None = None

    requirement_analysis: list[RequirementAnalysisItem] = Field(default_factory=list)

    evidence_items: ResumeEvidence | None = None

    matching_explanation: str = ""

    ai_fallback: AIFallback | None = None

    ai_analysis: AIAnalysisResponse | None = None
    ai_suggested_score: int | None = Field(default=None, ge=0, le=100)
    ai_score_rationale: str | None = None
    ai_confidence: int | None = Field(default=None, ge=0, le=100)
    local_fallback_used: bool = Field(default=False, serialization_alias="fallback_local_usado")
    contextual_requirements: list[AIRequirementAnalysis] = Field(default_factory=list)
    contextual_gaps: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    anti_fabrication_alerts: list[str] = Field(default_factory=list)
    attempted_providers: list[str] = Field(default_factory=list)
    sanitized_provider_errors: list[str] = Field(default_factory=list)
    provider_error_details: list[SanitizedProviderError] = Field(default_factory=list)
    job_level: str = "not_provided"
    ai_validation_applied: bool = False
    ai_validation_adjustments: list[str] = Field(default_factory=list)
    recommended_final_score: int | None = Field(default=None, ge=0, le=100)
    final_score_explanation: str | None = None
    keyword_report: KeywordReport | None = None
    score_keyword_coverage: int | None = Field(default=None, ge=0, le=100)
    weighted_present_keywords: list[ItemKeyword] = Field(default_factory=list)
    weighted_missing_keywords: list[ItemKeyword] = Field(default_factory=list)
    keyword_coverage_explanation: str | None = None
    fact_bank: FactBank | None = None
    ai_roles: list[str] = Field(default_factory=list)
    ai_context_quality: int | None = Field(default=None, ge=0, le=100)
    relevance_evaluation: dict | None = None
    evidence_matrix: list[dict] = Field(default_factory=list)
    prioritized_gaps: list[dict] = Field(default_factory=list)
    safe_rewrite_suggestions: list[str] = Field(default_factory=list)
    ats_diagnostics: dict | None = None
    contextual_ai_score: int | None = Field(default=None, ge=0, le=100)
    final_score_factors: dict[str, float | int | str | bool] = Field(default_factory=dict)
    final_score_alerts: list[str] = Field(default_factory=list)
    ai_pipeline: AIPipelineResult | None = None
    executed_ai_steps: list[str] = Field(default_factory=list)
    fallback_ai_steps: list[str] = Field(default_factory=list)
    job_relevant_evidence: list[SelectedEvidence] = Field(default_factory=list)
    ai_job_classification: AIJobClassification | None = None
    contextual_requirement_evaluations: list[ContextualRequirementEvaluation] = Field(default_factory=list)
    ai_pipeline_confidence: int | None = Field(default=None, ge=0, le=100)
    requirement_groups: list[RequirementGroup] = Field(default_factory=list)
    score_by_group: dict[str, int] = Field(default_factory=dict)
    grouped_semantic_score: int | None = Field(default=None, ge=0, le=100)
    sanitized_pipeline_errors: list[str] = Field(default_factory=list)
    pipeline_fallback_details: list[dict] = Field(default_factory=list)
    parser_warnings: list[str] = Field(default_factory=list)
    detected_sections: list[str] = Field(default_factory=list)
    low_confidence_sections: list[str] = Field(default_factory=list)
    evidence_source_summary: dict[str, int] = Field(default_factory=dict)
    sanitization_summary: dict[str, object] = Field(default_factory=dict)


class AIComplement(BaseModel):
    """Minimal AI-provider complement."""

    generated_summary: str = Field(min_length=1)

    suggestions: list[str] = Field(min_length=1)
