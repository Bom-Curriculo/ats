import asyncio

from app.providers.base import AIProviderError
from app.providers.mock import MockProvider
from app.schemas.analysis import FactBank, ItemKeyword, KeywordReport, AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai, calculate_final_score
from app.services.ai_orchestrator import run_ai_pipeline, prepare_ai_context
from app.services.evidence_selection import select_relevant_evidence_for_job


def input_request():
    return AnalysisRequest(
        resume_text="PROJETOS\nAPI FastAPI com Docker\nCURSOS\nSpring Boot\nCOMPETÊNCIAS\nKubernetes",
        job_text="Vaga júnior backend: FastAPI, Docker, Spring Boot e Kubernetes",
    )


def responses_pipeline():
    return {
        "job_classification": {"title": "Backend", "seniority": "junior", "area": "software", "core_requirements": ["FastAPI", "Docker"], "confidence": 90},
        "evaluation_contextual": {"evaluations": [
            {"item": "Spring Boot", "status": "found_with_evidence", "used_evidence": {"item": "Spring Boot", "source": "curso/formação", "evidence_level": "pratica_forte"}, "real_gap": False, "description_gap": False, "recommendation_safe": "Declare experiência forte.", "hallucination_risk": "high"}
        ], "contextual_ai_score": 88, "confidence": 90},
        "safe_suggestions": {"suggestions": ["Detalhe apenas usos comprovados."], "next_steps": []},
    }


def test_ai_orchestrator_behavior_01():
    request = input_request()
    provider = MockProvider(task_responses=responses_pipeline())
    result = asyncio.run(analyze_resume_with_ai(request, provider))
    assert result.ai_pipeline is not None
    assert result.executed_ai_steps[-1] == "consolidate_ai_response"
    spring = next(x for x in result.contextual_requirement_evaluations if x.item == "Spring Boot")
    kube = next(x for x in result.contextual_requirement_evaluations if x.item == "Kubernetes")
    assert spring.status == "found_without_clear_context"
    assert spring.used_evidence.evidence_level == "educacional"
    assert kube.status == "found_without_clear_context"
    assert kube.used_evidence.evidence_level == "skill_solta"
    assert len(provider.task_prompts) == 3


def test_ai_orchestrator_behavior_02():
    responses = responses_pipeline()
    responses["evaluation_contextual"] = AIProviderError("falha", category="timeout")
    result = asyncio.run(analyze_resume_with_ai(input_request(), MockProvider(task_responses=responses)))
    assert "evaluate_requirements_contextually" in result.fallback_ai_steps
    assert result.local_fallback_used is False
    assert result.contextual_requirement_evaluations
    detail = next(x for x in result.pipeline_fallback_details if x["step"] == "evaluate_requirements_contextually")
    assert detail == {
        "step": "evaluate_requirements_contextually", "error_category": "timeout",
        "safe_message": "A etapa excedeu o tempo limite.", "provider": "mock",
        "model": "modelo-mock", "schema_used": "EvaluationsResponse",
    }
    assert result.sanitized_pipeline_errors == ["A etapa excedeu o tempo limite."]


def test_ai_orchestrator_behavior_03():
    evidence_items = [{"item": "Python", "source": "project", "evidence": f"ana@example.com evidência {i} Python"} for i in range(40)]
    fb = FactBank(evidence_items=evidence_items)
    report = KeywordReport(hard_skills=[ItemKeyword(term="Python", category="hard_skills", weight=2, present=True)])
    selected = select_relevant_evidence_for_job(fb, ["Python"], report)
    assert len(selected) <= 20
    assert all(len(x.excerpt or "") <= 500 and "ana@example.com" not in (x.excerpt or "") for x in selected)

    local = analyze_resume(input_request())
    context = prepare_ai_context(input_request(), local)
    assert "fact_bank" not in context


def test_ai_orchestrator_behavior_04():
    provider = MockProvider(task_responses=responses_pipeline())
    local = analyze_resume(input_request())
    asyncio.run(run_ai_pipeline(input_request(), local, provider))
    prompts = "\n".join(p for _, p in provider.task_prompts)
    assert '"selected_evidence"' in prompts
    assert '"technologies_by_source"' not in prompts
    assert "ana@example.com" not in prompts


def test_ai_orchestrator_behavior_05():
    complete, _ = calculate_final_score(40, 95, 90, 0, "junior", True, 50, 0, 90, 0)
    degraded, explanation = calculate_final_score(40, 95, 90, 0, "junior", True, 50, 0, 90, 2)
    assert degraded < complete
    assert "etapas com fallback 2" in explanation


def test_ai_orchestrator_behavior_06():
    result = asyncio.run(analyze_resume_with_ai(input_request(), MockProvider(task_responses=responses_pipeline())))
    assert result.ats_score is not None
    assert result.matched_keywords is not None
    assert result.recommended_final_score is not None
    assert result.contextual_requirements is not None
