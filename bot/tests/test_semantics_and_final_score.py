import asyncio

import pytest

from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai
from app.services.matching.technical_equivalences import JobLevel, detect_job_level


def analyze(cv: str, job: str):
    return analyze_resume(AnalysisRequest(resume_text=cv, job_text=job))


@pytest.mark.parametrize(
    ("origin", "requirement"),
    [("Next.js", "React"), ("Spring Boot", "Java"), ("FastAPI", "Python"),
     ("Laravel", "PHP"), ("NestJS", "TypeScript"), ("ASP.NET Core", "C#"),
     ("Docker Compose", "Docker")],
)
def test_inferences_strong_not_invent_practice(origin, requirement):
    result = analyze(f"COMPETÊNCIAS\n{origin}", f"Requisitos:\n{requirement}")
    item = result.requirement_analysis[0]
    assert item.status == "related_but_not_explicit"
    assert item.inference_strength == "implicacao_forte"


def test_semantics_and_final_score_behavior_02():
    result = analyze("PROJETOS\nSite feito com HTML e CSS", "Requisitos:\nHTML5 e CSS3")
    assert {i.item: i.status for i in result.requirement_analysis} == {
        "HTML": "found_with_evidence", "CSS": "found_with_evidence"
    }


def test_semantics_and_final_score_behavior_03():
    course = analyze("CURSOS\nJava Moderno com Spring Boot", "Vaga júnior\nSpring Boot")
    project = analyze("PROJETOS\nAPI construída com Spring Boot", "Vaga júnior\nSpring Boot")
    assert course.requirement_analysis[0].evidence_level == "educational_evidence"
    assert course.requirement_analysis[0].status == "found_without_clear_context"
    assert project.requirement_analysis[0].status == "found_with_evidence"


def test_semantics_and_final_score_behavior_04():
    result = analyze(
        "COMPETÊNCIAS\nSQL", "Requisitos:\nSQL, SELECT, JOIN, WHERE, INSERT, UPDATE e DELETE"
    )
    assert all(i.status != "missing" for i in result.requirement_analysis)
    text = " ".join(result.suggestions).lower()
    assert text.count("select") <= 1
    assert text.count("join") <= 1


def test_semantics_and_final_score_behavior_05():
    docker = analyze("PROJETOS\nDocker", "Requisitos:\nKubernetes")
    tailwind = analyze("PROJETOS\nTailwind", "Requisitos:\nCSS")
    chatgpt = analyze("Uso ChatGPT", "Requisitos:\nAPIs de IA")
    assert docker.requirement_analysis[0].status == "missing"
    assert tailwind.requirement_analysis[0].status == "related_but_not_explicit"
    assert chatgpt.requirement_analysis[0].status == "missing"


def test_semantics_and_final_score_behavior_06():
    result = analyze("PROJETOS\nIntegração feita com OpenAI API", "Requisitos:\nAPIs de IA")
    item = next(i for i in result.requirement_analysis if i.item == "APIs de IA")
    assert item.status == "related_but_not_explicit"
    assert item.inference_strength == "implicacao_forte"


def test_semantics_and_final_score_behavior_07():
    result = analyze("IDIOMAS\nInglês para leitura de documentação", "Inglês técnico")
    assert result.requirement_analysis[0].status != "missing"


def test_semantics_and_final_score_behavior_08():
    assert detect_job_level("Estágio em desenvolvimento") == JobLevel.INTERNSHIP
    estagio = analyze("CURSOS\nSpring Boot", "Estágio\nSpring Boot")
    senior = analyze("CURSOS\nSpring Boot", "Desenvolvedor sênior\nSpring Boot")
    assert estagio.ats_score > senior.ats_score
    assert estagio.valid_analysis is True


def test_semantics_and_final_score_behavior_09():
    result = analyze_resume(AnalysisRequest(
        resume_text="CURSOS\nSpring Boot", job_text="Spring Boot", job_level="sênior"
    ))
    assert result.job_level == "senior"
    assert result.ats_score == 15


def ai_response(status_html="missing", status_spring="found_with_evidence", score=90):
    def req(item, status):
        return {"item": item, "category": "technical_skill", "importance": "required",
                "status": status, "evidence": item, "rationale": "Avaliação externa.",
                "recommendation": "Descreva apenas evidência real."}
    return {"contextual_summary": "Análise concluída.",
            "contextual_requirements": [req("HTML5", status_html), req("Spring Boot", status_spring)],
            "strengths": [], "gaps": ["HTML5"], "possible_blockers": [],
            "improvement_suggestions": ["Detalhe as tecnologias usadas."], "next_steps": [],
            "anti_fabrication_alerts": ["Não invente."], "confidence": 95,
            "ai_suggested_score": score, "ai_score_rationale": "Boa aderência."}


def test_semantics_and_final_score_behavior_10():
    input_request = AnalysisRequest(
        resume_text="PROJETOS\nSite com HTML\nCURSOS\nSpring Boot",
        job_text="Vaga júnior\nHTML5 e Spring Boot",
    )
    result = asyncio.run(analyze_resume_with_ai(
        input_request, MockProvider(structured_response=ai_response())
    ))
    status = {i.item: i.status for i in result.contextual_requirements}
    assert status["HTML5"] == "found_with_evidence"
    assert status["Spring Boot"] == "found_without_clear_context"
    assert result.ai_validation_applied is True
    assert len(result.ai_validation_adjustments) == 2
    assert result.recommended_final_score is not None
    assert result.final_score_explanation


def test_semantics_and_final_score_behavior_11():
    input_request = AnalysisRequest(resume_text="Python", job_text="Python")
    result = asyncio.run(analyze_resume_with_ai(
        input_request, MockProvider(simulated_error=RuntimeError("falha"))
    ))
    assert result.local_fallback_used is True
    assert result.recommended_final_score == result.ats_score
