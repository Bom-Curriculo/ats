import asyncio
import json

from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai
from app.services.privacy.sanitizer import PrivacySanitizer


FAKE_RESUME = """Pessoa Exemplo
E-mail: pessoa.teste@gmail.example
Telefone: (81) 99999-1234
CPF: 123.456.789-09
LinkedIn: https://linkedin.com/in/pessoa-exemplo
GitHub: https://github.com/pessoa-exemplo
Portfólio: https://portfolio.example.dev
Endereço: Rua Exemplo, 123, Bairro Teste
PROJETOS
Serviço Web
Stack: Python 3.12, FastAPI, .NET 9, Java 17
- API publicada com testes
Repositório: https://github.com/pessoa-exemplo/servico-web
Deploy: https://servico-web.vercel.app
FORMAÇÃO
Curso Superior | 2020 - 2023
"""


def test_sanitization_classifies_links_without_returning_values():
    result = PrivacySanitizer().sanitize(FAKE_RESUME)
    assert {"email", "phone", "cpf", "linkedin_url", "github_profile_url",
            "portfolio_url", "github_repo_url", "deploy_url", "address"} <= set(result.items_removed)
    assert result.links_detected_by_type == {
        "linkedin_url": 1, "github_profile_url": 1, "portfolio_url": 1,
        "github_repo_url": 1, "deploy_url": 1,
    }
    for value in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "portfolio.example.dev", "vercel.app", "Rua Exemplo"):
        assert value not in result.text_sanitized
    assert "[EMAIL_REMOVED]" in result.text_sanitized
    assert "[PORTFOLIO_REMOVED]" in result.text_sanitized
    assert "[URL_REMOVED]" in result.text_sanitized


def test_synthetic_resume_privacy_behavior_02():
    safe = PrivacySanitizer().sanitize(FAKE_RESUME).text_sanitized
    for value in ("2020 - 2023", ".NET 9", "Java 17", "Python 3.12", "FastAPI"):
        assert value in safe


class MockCapturaSeguro(MockProvider):
    received = None

    async def generate_structured_analysis(self, safe_request, local_result):
        self.received = safe_request
        return {
            "contextual_summary": "Análise segura.", "contextual_requirements": [],
            "strengths": ["Python"], "gaps": [], "possible_blockers": [],
            "improvement_suggestions": ["Detalhe o project real."], "next_steps": [],
            "anti_fabrication_alerts": ["Não invente."], "confidence": 80,
        }


def test_synthetic_resume_privacy_behavior_03():
    provider = MockCapturaSeguro()
    input_request = AnalysisRequest(
        resume_text=FAKE_RESUME,
        job_text="Contato: recrutador@example.com\nRequisitos: Python e FastAPI",
        resume_sources=[{"type": "github_url", "url": "https://github.com/pessoa-exemplo"}],
    )
    result = asyncio.run(analyze_resume_with_ai(input_request, provider))
    sent = provider.received.resume_text + provider.received.job_text
    assert provider.received.resume_sources == []
    for value in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "recrutador@example.com"):
        assert value not in sent
    assert result.privacy.ai_text_was_sanitized is True


def test_synthetic_resume_privacy_behavior_04():
    result = analyze_resume(AnalysisRequest(
        resume_text=FAKE_RESUME, job_text="Requisitos: Python, FastAPI, .NET e Java"
    ))
    serialized = json.dumps(result.model_dump(), ensure_ascii=False)
    for value in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "portfolio.example.dev", "Rua Exemplo"):
        assert value not in serialized
    assert {"Python", "FastAPI", ".NET", "Java"} <= set(result.matched_keywords)
    summary = result.sanitization_summary
    assert summary.sensitive_data_detected is True
    assert summary.category_count >= 5
    assert summary.links_detected_by_type["github_repo_url"] == 1
    assert "pessoa" not in summary.safe_note.casefold()


def test_synthetic_resume_privacy_behavior_05():
    input_request = AnalysisRequest(
        resume_sources=[{"type": "curriculo_texto", "content": "PROJETOS\nAPI\nStack: Python"}],
        job_text="Requisitos: Python",
    )
    assert "Python" in input_request.resume_text
    result = analyze_resume(input_request)
    assert "Python" in result.matched_keywords
