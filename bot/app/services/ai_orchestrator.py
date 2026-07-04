import os

from pydantic import BaseModel, Field

from app.providers.base import AIProvider
from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.schemas.ai_pipeline import (
    ContextualRequirementEvaluation, AIJobClassification, AIPipelineResult,
)
from app.services.ai_context import build_ai_context
from app.services.text_normalizer import normalize_for_comparison
from app.services.ai_pipeline_prompts import (
    prompt_contextual_evaluation, prompt_job_classification, prompt_safe_suggestions,
)
from app.services.evidence_selection import select_relevant_evidence_for_job


STEPS = ["prepare_ai_context", "classify_job", "select_relevant_evidence",
          "evaluate_requirements_contextually", "prioritize_gaps",
          "generate_safe_suggestions", "consolidate_ai_response"]

ERROR_MESSAGES = {
    "timeout": "A etapa excedeu o tempo limite.", "rate_limit_429": "O provider limitou a etapa.",
    "request_too_large": "O contexto da etapa excedeu o limite.", "invalid_json": "A etapa retornou JSON inválido.",
    "json_truncated": "A etapa retornou JSON truncado.", "empty_response": "A etapa retornou resposta vazia.",
    "schema_validation_error": "A resposta não corresponde ao schema da etapa.",
    "unsupported_task_api": "O provider não implementa tarefas estruturadas.",
    "unknown_provider_error": "A etapa falhou e usou análise local.",
}


def _fallback_detail(step: str, provider: AIProvider, schema: type, error: Exception | None = None) -> dict:
    category = getattr(error, "category", None) or ("unsupported_task_api" if error is None else "unknown_provider_error")
    return {"step": step, "error_category": category,
            "safe_message": ERROR_MESSAGES.get(category, ERROR_MESSAGES["unknown_provider_error"]),
            "provider": provider.name, "model": provider.model,
            "schema_used": schema.__name__}


class EvaluationsResponse(BaseModel):
    evaluations: list[ContextualRequirementEvaluation] = Field(default_factory=list)

    contextual_ai_score: int | None = Field(default=None, ge=0, le=100)
    confidence: int | None = Field(default=None, ge=0, le=100)


class SuggestionsResponse(BaseModel):

    suggestions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


def get_task_model_policy() -> dict[str, str]:
    """Parse the optional per-task provider policy."""
    politica = {"job_classification": "rapido", "evaluation_contextual": "principal",
                "safe_suggestions": "principal", "fallback": "local"}
    for parte in os.getenv("IA_TASK_PROVIDER_POLICY", "").split(","):
        if "=" in parte:
            task, perfil = (x.strip().lower() for x in parte.split("=", 1))
            if task in politica and perfil:
                politica[task] = perfil
    return politica


def prepare_ai_context(request: AnalysisRequest, result: AnalysisResult) -> dict:
    context = build_ai_context(request, result)
    # Implementation note.
    context.pop("fact_bank", None)
    return context


def _local_classification(result: AnalysisResult) -> AIJobClassification:
    report = result.keyword_report
    centrais = [x.item for x in result.requirement_analysis if x.weight >= 2]
    secundarios = [x.item for x in result.requirement_analysis if x.weight < 2]
    return AIJobClassification(
        title=str((result.relevance_evaluation or {}).get("title_detectado") or "") or None,
        seniority=result.job_level, core_requirements=centrais,
        secondary_requirements=secundarios,
        differentials=[x.item for x in result.requirement_analysis if x.category == "differential"],
        hard_filters=[x.term for x in report.hard_filters] if report else [],
        business_context=[x.term for x in report.business_context] if report else [], confidence=75,
        company=(result.relevance_evaluation or {}).get("company") or None,
        area=(result.relevance_evaluation or {}).get("area") or None,
        technologies=[x.item for x in result.requirement_analysis if x.type == "technology"],
        responsibilities=[], modality=(result.relevance_evaluation or {}).get("modality") or None,
        location=(result.relevance_evaluation or {}).get("location") or None,
        accepts_no_experience=bool((result.relevance_evaluation or {}).get("accepts_no_experience")),
    )


async def classify_job(context: dict, result: AnalysisResult, provider: AIProvider) -> tuple[AIJobClassification, bool]:
    local = _local_classification(result)
    prompt = prompt_job_classification(context.get("summary_job_sanitized", ""), {
        "level": result.job_level, "requirements": local.core_requirements + local.secondary_requirements,
        "hard_filters": local.hard_filters}, AIJobClassification.model_json_schema())
    try:
        raw = await provider.run_structured_task("job_classification", prompt, AIJobClassification, 0.1)
        return (AIJobClassification.model_validate(raw), False, None) if raw else (local, True, _fallback_detail("classify_job", provider, AIJobClassification))
    except Exception as error:
        return local, True, _fallback_detail("classify_job", provider, AIJobClassification, error)


def select_relevant_evidence(result: AnalysisResult, classification: AIJobClassification):
    return select_relevant_evidence_for_job(
        result.fact_bank, result.requirement_analysis, result.keyword_report,
        classification.seniority or result.job_level)


def _local_evaluations(result: AnalysisResult, evidence_items: list) -> list[ContextualRequirementEvaluation]:
    por_item = {}
    for evidence in evidence_items:
        por_item.setdefault(normalize_for_comparison(evidence.item), evidence)
    output = []
    for item in result.requirement_analysis:
        evidence = por_item.get(normalize_for_comparison(item.item))
        absent = item.status == "missing"
        descricao = item.status in {"found_without_clear_context", "related_but_not_explicit"}
        output.append(ContextualRequirementEvaluation(
            item=item.item, importance="required" if item.weight >= 3 else "desired",
            job_relevance="high" if item.weight >= 2 else "medium", status=item.status,
            used_evidence=evidence, real_gap=absent, description_gap=descricao,
            recommendation_safe=item.guidance,
            hallucination_risk="high" if absent else ("medium" if descricao else "low")))
    return output


async def evaluate_requirements_contextually(result: AnalysisResult, classification: AIJobClassification,
                                              evidence_items: list, provider: AIProvider):

    local = _local_evaluations(result, evidence_items)
    prompt = prompt_contextual_evaluation(classification.model_dump(),
        [{"item": x.item, "weight": x.weight, "status_local": x.status} for x in result.requirement_analysis],
        [x.model_dump() for x in evidence_items], EvaluationsResponse.model_json_schema())

    try:
        raw = await provider.run_structured_task("evaluation_contextual", prompt, EvaluationsResponse, 0.1)
        if not raw:
            return local, result.ats_score, 70, True, _fallback_detail("evaluate_requirements_contextually", provider, EvaluationsResponse)
        response = EvaluationsResponse.model_validate(raw)


        # Technical note removed during English standardization.
        externas = {normalize_for_comparison(x.item): x for x in response.evaluations}
        conciliadas = []
        for local in local:
            external = externas.get(normalize_for_comparison(local.item))
            if external:
                local = local.model_copy(update={
                    "job_relevance": external.job_relevance,
                    "recommendation_safe": external.recommendation_safe or local.recommendation_safe,
                    "hallucination_risk": max(local.hallucination_risk, external.hallucination_risk),
                })
            conciliadas.append(local)
        return conciliadas, response.contextual_ai_score or result.ats_score, response.confidence or 70, False, None
    except Exception as error:
        return local, result.ats_score, 60, True, _fallback_detail("evaluate_requirements_contextually", provider, EvaluationsResponse, error)


def prioritize_gaps(evaluations: list[ContextualRequirementEvaluation]) -> list[dict]:
    prioridade = {"high": 3, "medium": 2, "low": 1}
    gaps = [{"item": x.item, "prioridade": x.job_relevance,
                "real_gap": x.real_gap, "description_gap": x.description_gap,
                "recommendation": x.recommendation_safe} for x in evaluations if x.real_gap or x.description_gap]
    return sorted(gaps, key=lambda x: -prioridade.get(x["prioridade"], 0))


async def generate_safe_suggestions(evaluations: list[ContextualRequirementEvaluation], gaps: list[dict], provider: AIProvider):
    local = list(dict.fromkeys(x.recommendation_safe for x in evaluations if x.recommendation_safe))[:12]
    prompt = prompt_safe_suggestions([x.model_dump() for x in evaluations], gaps, SuggestionsResponse.model_json_schema())


    try:
        raw = await provider.run_structured_task("safe_suggestions", prompt, SuggestionsResponse, 0.1)
        if not raw:
            return local, [], True, _fallback_detail("generate_safe_suggestions", provider, SuggestionsResponse)
        response = SuggestionsResponse.model_validate(raw)

        # Technical note removed during English standardization.
        #
        #
        return response.suggestions[:12], response.next_steps[:12], False, None
    except Exception as error:
        return local, [], True, _fallback_detail("generate_safe_suggestions", provider, SuggestionsResponse, error)


def consolidate_ai_response(result: AnalysisResult, pipeline: AIPipelineResult,
                           next_steps: list[str]) -> AIAnalysisResponse:
    category = {"technology": "technical_skill", "requirement": "other"}
    requirements = [AIRequirementAnalysis(
        item=x.item, category=category.get(next((i.type for i in result.requirement_analysis if i.item == x.item), "requirement"), "other"),
        importance=x.importance if x.importance in {"required", "desired", "differential", "contextual", "not_provided"} else "not_provided",
        status=x.status if x.status in {"found_with_evidence", "found_without_clear_context", "related_but_not_explicit", "missing", "not_evaluated", "possible_blocker"} else "not_evaluated",
        evidence=x.used_evidence.excerpt if x.used_evidence else None,
        rationale="Avaliação conciliada com evidência local selecionada.", recommendation=x.recommendation_safe or "Confirme a evidência antes de alterar o currículo.")
        for x in pipeline.requirement_evaluations]
    return AIAnalysisResponse(
        contextual_summary="Análise contextual em etapas, conciliada com evidências locais.",
        contextual_requirements=requirements,
        strengths=[x.item for x in pipeline.requirement_evaluations if x.status == "found_with_evidence"],
        gaps=[x.item for x in pipeline.requirement_evaluations if x.real_gap],
        possible_blockers=result.keyword_report.hard_filter_alerts if result.keyword_report else [],
        improvement_suggestions=pipeline.safe_suggestions, next_steps=next_steps,
        anti_fabrication_alerts=["Não transforme curso, skill isolada ou tecnologia absent em experiência prática."],
        confidence=pipeline.pipeline_confidence or 50, ai_suggested_score=pipeline.contextual_ai_score,
        ai_score_rationale="Score contextual calculado sobre requisitos e evidências selected.",
        ai_roles=["classificadora da vaga", "auditora de evidências", "revisora anti-alucinação"],
        ai_context_quality=pipeline.pipeline_confidence,
        evidence_matrix=[x.model_dump() for x in pipeline.relevant_evidence],
        prioritized_gaps=pipeline.prioritized_gaps,
        safe_rewrite_suggestions=pipeline.safe_suggestions,
        contextual_ai_score=pipeline.contextual_ai_score)


async def run_ai_pipeline(request: AnalysisRequest, result: AnalysisResult,
                               provider: AIProvider) -> tuple[AIPipelineResult, AIAnalysisResponse]:
    executadas, fallbacks, details = [], [], []
    context = prepare_ai_context(request, result); executadas.append(STEPS[0])
    classification, fallback, detail = await classify_job(context, result, provider); executadas.append(STEPS[1])
    if fallback: fallbacks.append(STEPS[1]); details.append(detail)
    evidence_items = select_relevant_evidence(result, classification); executadas.append(STEPS[2])
    evaluations, score, confidence, fallback, detail = await evaluate_requirements_contextually(result, classification, evidence_items, provider); executadas.append(STEPS[3])
    if fallback: fallbacks.append(STEPS[3]); details.append(detail)
    gaps = prioritize_gaps(evaluations); executadas.append(STEPS[4])
    suggestions, passos, fallback, detail = await generate_safe_suggestions(evaluations, gaps, provider); executadas.append(STEPS[5])
    if fallback: fallbacks.append(STEPS[5]); details.append(detail)
    pipeline_confidence = max(20, round(confidence - len(fallbacks) * 12))
    pipeline = AIPipelineResult(job_classification=classification, relevant_evidence=evidence_items,
        requirement_evaluations=evaluations, prioritized_gaps=gaps, safe_suggestions=suggestions,
        contextual_ai_score=score, pipeline_confidence=pipeline_confidence,
        executed_steps=executadas + [STEPS[6]], fallback_steps=fallbacks,
        fallback_details=[x for x in details if x])
    return pipeline, consolidate_ai_response(result, pipeline, passos)
