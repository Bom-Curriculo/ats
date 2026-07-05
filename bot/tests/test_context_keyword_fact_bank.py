
import asyncio

from app.providers.base import create_prompt
from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai, calculate_final_score


def analyze(cv: str, job: str):
    return analyze_resume(AnalysisRequest(resume_text=cv, job_text=job))


def test_context_keyword_fact_bank_behavior_01():

    result = analyze("COMPETÊNCIAS\nPython", "Vaga backend\nPython, Docker e contexto financeiro")
    assert result.keyword_report is not None
    python = next(x for x in result.keyword_report.hard_skills if x.term == "Python")
    docker = next(x for x in result.weighted_missing_keywords if x.term == "Docker")
    assert python.weight == 2.0 and docker.weight == 2.0
    assert result.score_keyword_coverage is not None


def test_context_keyword_fact_bank_behavior_02():
    result = analyze("PROJETOS\nAPI em Python", "Obrigatório: graduação completa e Python")
    assert result.keyword_report.hard_filter_alerts
    assert any("hard filter" in x for x in result.final_score_alerts)


def test_context_keyword_fact_bank_behavior_03():
    result = analyze(
        "EXPERIÊNCIA PROFISSIONAL\nPython\nPROJETOS\nFastAPI e Docker\nCURSOS\nSpring Boot\nCOMPETÊNCIAS\nGit",
        "Python FastAPI Docker Spring Boot Git",
    )

    fb = result.fact_bank
    assert fb.experiences and fb.projects and fb.courses and fb.skills
    assert "FastAPI" in fb.technologies_by_source["project"]
    assert "Docker" in fb.technologies_by_source["project"]

    assert "Spring Boot" in fb.technologies_by_source["curso/formação"]
    spring = next(x for x in result.requirement_analysis if x.item == "Spring Boot")
    assert spring.evidence_level == "educational_evidence"


def fabricated_response():
    return {
        "contextual_summary": "Análise.",
        "contextual_requirements": [{"item": "Kubernetes", "category": "tool", "importance": "required", "status": "found_with_evidence", "evidence": "Kubernetes em produção", "rationale": "Consta.", "recommendation": "Destaque."}],
        "strengths": ["Kubernetes"], "gaps": [], "possible_blockers": [],
        "improvement_suggestions": ["Inclua Kubernetes na experiência."], "next_steps": [],
        "anti_fabrication_alerts": [], "confidence": 95, "ai_suggested_score": 95,
    }


def test_context_keyword_fact_bank_behavior_04():
    input_request = AnalysisRequest(resume_text="PROJETOS\nDocker", job_text="Kubernetes")

    result = asyncio.run(analyze_resume_with_ai(input_request, MockProvider(structured_response=fabricated_response())))

    req = result.contextual_requirements[0]
    assert req.status == "missing" and req.evidence is None

    assert result.ai_analysis.strengths == []
    assert any("Ponto forte sem evidência" in x for x in result.ai_validation_adjustments)
    assert any("Estude ou crie um project" in x for x in result.next_steps)


def test_context_keyword_fact_bank_behavior_05():
    poucos, _ = calculate_final_score(40, 100, 95, 0, "junior", False, 60)

    muitos, explanation = calculate_final_score(40, 100, 95, 4, "junior", False, 60)

    sem_keywords, _ = calculate_final_score(40, 100, 95, 4, "junior", False, None)
    assert muitos < poucos and muitos != sem_keywords
    assert "correções 4" in explanation


def test_context_keyword_fact_bank_behavior_06():
    input_request = AnalysisRequest(resume_text="COMPETÊNCIAS\nDocker", job_text="Kubernetes")
    local = analyze_resume(input_request)
    prompt = create_prompt(input_request, local)


    assert '"fact_bank"' in prompt and "An isolated skill is never practical." in prompt

    assert "Docker with Kubernetes" in prompt
