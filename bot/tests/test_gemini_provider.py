import asyncio
import json

import httpx
import pytest
from app.providers.base import AIProviderError
from app.providers.gemini import GeminiProvider, extract_gemini_text
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume
from app.services.ai_manager import run_analysis_with_fallback
from app.schemas.ai_pipeline import AIJobClassification


def structured_response() -> dict:
    return {
        "contextual_summary": "Compatibilidade analisada sem inventar experiência.",
        "contextual_requirements": [],
        "strengths": ["Python aparece no currículo."],
        "gaps": ["FastAPI não aparece no currículo."],
        "possible_blockers": [],
        "improvement_suggestions": ["Detalhe projects reais."],
        "next_steps": ["Estude FastAPI antes de declarar experiência."],
        "anti_fabrication_alerts": ["Não declarar habilidades missing_items."],
        "confidence": 85,
        "ai_suggested_score": None,
        "ai_score_rationale": None,
    }


def envelope_gemini(text: str) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": text}],
                    "role": "model",
                }
            }
        ]
    }


class RespostaHTTPFake:
    def __init__(self, status: int, corpo: dict):
        self.status_code = status
        self.corpo = corpo
        self.request = httpx.Request("POST", "https://gemini.test")

    def json(self):
        return self.corpo

    def raise_for_status(self):
        if self.status_code >= 400:
            response = httpx.Response(
                self.status_code, request=self.request, json=self.corpo
            )
            raise httpx.HTTPStatusError(
                "erro HTTP simulado", request=self.request, response=response
            )


class ClienteHTTPFake:
    response: RespostaHTTPFake
    last_call: dict | None = None

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, **kwargs):
        type(self).last_call = {"url": url, **kwargs}
        return type(self).response


def provider() -> GeminiProvider:
    return GeminiProvider("chave-ficticia-para-teste", "gemini-2.5-flash")


def local_base():
    request = AnalysisRequest(
        resume_text="HABILIDADES\nPython",
        job_text="Requisitos:\nPython e FastAPI",
    )
    return request, analyze_resume(request)


def test_gemini_provider_behavior_01() -> None:
    response = envelope_gemini('{"resumo_analise":"ok"}')

    assert extract_gemini_text(response) == '{"resumo_analise":"ok"}'


def test_gemini_provider_behavior_02(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.response = RespostaHTTPFake(
        200, envelope_gemini("```json\n" + json.dumps(structured_response()) + "\n```")
    )
    request, result = local_base()

    analysis = asyncio.run(provider().generate_structured_analysis(request, result))

    assert analysis.confidence == 85
    call = ClienteHTTPFake.last_call
    assert call["params"] == {"key": "chave-ficticia-para-teste"}
    assert "response_format" not in call["json"]
    assert call["json"]["generationConfig"] == {"temperature": 0.2}


@pytest.mark.parametrize(
    "status,category",
    [(429, "rate_limit_429"), (413, "request_too_large")],
)
def test_gemini_classifies_errors_http(monkeypatch, status, category) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.response = RespostaHTTPFake(
        status, {"error": {"status": "simulado"}}
    )
    request, result = local_base()

    with pytest.raises(AIProviderError) as captured:
        asyncio.run(provider().generate_structured_analysis(request, result))

    assert captured.value.category == category
    assert captured.value.status_http == status


def test_gemini_provider_behavior_04(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    monkeypatch.setenv("IA_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    ClienteHTTPFake.response = RespostaHTTPFake(
        200, envelope_gemini(json.dumps(structured_response()))
    )
    request, _ = local_base()

    result = asyncio.run(run_analysis_with_fallback(request))

    assert result.local_fallback_used is False
    assert result.ai_provider == "gemini"
    assert result.ai_model == "gemini-2.5-flash"
    assert result.ai_analysis is not None


def test_gemini_provider_behavior_05(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    monkeypatch.setenv("IA_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    ClienteHTTPFake.response = RespostaHTTPFake(429, {"error": {}})
    request, local = local_base()

    result = asyncio.run(run_analysis_with_fallback(request))

    assert result.local_fallback_used is True
    assert result.ats_score == local.ats_score
    assert result.provider_error_details[0].error_category == "rate_limit_429"


@pytest.mark.parametrize(
    "text,category",
    [
        ("não-json", "invalid_json"),
        ('{"titulo":"Backend"', "json_truncated"),
        ("", "empty_response"),
        ('{"confidence": 999}', "schema_validation_error"),
    ],
)
def test_gemini_provider_behavior_06(monkeypatch, text, category):
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.response = RespostaHTTPFake(200, envelope_gemini(text))
    with pytest.raises(AIProviderError) as captured:
        asyncio.run(provider().run_structured_task(
            "job_classification", "prompt curto", AIJobClassification, 0.1
        ))
    assert captured.value.category == category


def test_gemini_provider_behavior_07(monkeypatch):
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.response = RespostaHTTPFake(200, envelope_gemini(json.dumps({
        "title": "Backend", "seniority": "junior", "core_requirements": ["Python"], "confidence": 90
    })))
    response = asyncio.run(provider().run_structured_task(
        "job_classification", "prompt curto", AIJobClassification, 0.1
    ))
    assert response["title"] == "Backend" and response["confidence"] == 90
