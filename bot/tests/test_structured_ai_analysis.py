import asyncio

from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume_with_ai
from app.services.ats_analyzer import analyze_resume


def ai_response(**changes):
    base = {
        "contextual_summary": "Há aderência parcial comprovada.",
        "contextual_requirements": [],
        "strengths": ["Experiência descrita com Python."],
        "gaps": [],

        "possible_blockers": [],
        "improvement_suggestions": ["Detalhe o contexto de uso de Python."],
        "next_steps": ["Confirme habilidades antes de adicioná-las."],
        "anti_fabrication_alerts": ["Não declarar competências missing_items."],
        "confidence": 80,

        "ai_suggested_score": 95,
        "ai_score_rationale": "Leitura contextual complementar.",
    }
    base.update(changes)
    return base


def test_structured_ai_analysis_behavior_01() -> None:
    request = AnalysisRequest(
        resume_text="Experiência com Python.", job_text="Python e FastAPI"
    )
    local_score = 50
    result = asyncio.run(
        analyze_resume_with_ai(
            request, MockProvider(structured_response=ai_response())
        )
    )
    assert result.ats_score == local_score
    assert result.ai_suggested_score == 95
    assert result.ai_analysis is not None
    assert result.local_fallback_used is False


def test_structured_ai_analysis_behavior_02() -> None:
    request = AnalysisRequest(resume_text="Python", job_text="Python")
    score_local = analyze_resume(request).ats_score
    result = asyncio.run(
        analyze_resume_with_ai(
            request,
            MockProvider(structured_response="não é json"),
        )
    )

    # Implementation note.
    assert result.local_fallback_used is True
    assert result.ai_analysis is None
    assert result.ats_score == score_local


def test_structured_ai_analysis_behavior_03() -> None:
    requirement = {
        "item": "Kubernetes",
        "category": "tool",
        "importance": "required",
        "status": "found_with_evidence",
        "evidence": "Administrou Kubernetes",
        "rationale": "Suposta experiência.",
        "recommendation": "Destacar Kubernetes.",
    }
    result = asyncio.run(
        analyze_resume_with_ai(
            AnalysisRequest(resume_text="Experiência com Python", job_text="Kubernetes"),
            MockProvider(
                structured_response=ai_response(contextual_requirements=[requirement])
            ),
        )
    )
    validado = result.contextual_requirements[0]
    assert validado.status == "missing"
    assert validado.evidence is None
    assert "Kubernetes" in result.contextual_gaps


class MockCaptura(MockProvider):
    received = None

    async def generate_structured_analysis(self, safe_request, local_result):
        self.received = safe_request
        return ai_response()


def test_structured_ai_analysis_behavior_04() -> None:
    provider = MockCaptura()
    secret = "Bearer abcdefghijklmnopqrstuvwxyz123456"

    result = asyncio.run(

        analyze_resume_with_ai(
            AnalysisRequest(
                resume_text=(
                    "ana@example.com (81) 99999-1234 CPF 123.456.789-10 "

                    "https://linkedin.com/in/ana " + secret
                ),
                job_text="Contato recrutador@example.com https://empresa.example/vaga",
            ),
            provider,
        )
    )
    sent = provider.received.resume_text + provider.received.job_text
    # Implementation note.
    for value in ("ana@example.com", "99999-1234", "123.456.789-10", "linkedin.com", secret, "recrutador@example.com", "empresa.example"):
        assert value not in sent
    assert result.privacy.ai_text_was_sanitized is True
