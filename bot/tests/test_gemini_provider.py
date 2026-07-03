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


def resposta_estruturada() -> dict:
    return {
        "resumo_contextual": "Compatibilidade analisada sem inventar experiência.",
        "requisitos_contextuais": [],
        "pontos_fortes": ["Python aparece no currículo."],
        "lacunas": ["FastAPI não aparece no currículo."],
        "possiveis_impeditivos": [],
        "sugestoes_de_melhoria": ["Detalhe projetos reais."],
        "proximos_passos": ["Estude FastAPI antes de declarar experiência."],
        "alertas_contra_inventar": ["Não declarar habilidades ausentes."],
        "confianca": 85,
        "score_sugerido_ia": None,
        "justificativa_score_ia": None,
    }


def envelope_gemini(texto: str) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": texto}],
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
            resposta = httpx.Response(
                self.status_code, request=self.request, json=self.corpo
            )
            raise httpx.HTTPStatusError(
                "erro HTTP simulado", request=self.request, response=resposta
            )


class ClienteHTTPFake:
    resposta: RespostaHTTPFake
    ultima_chamada: dict | None = None

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, **kwargs):
        type(self).ultima_chamada = {"url": url, **kwargs}
        return type(self).resposta


def provider() -> GeminiProvider:
    return GeminiProvider("chave-ficticia-para-teste", "gemini-2.5-flash")


def base_local():
    solicitacao = AnalysisRequest(
        curriculo_texto="HABILIDADES\nPython",
        vaga_texto="Requisitos:\nPython e FastAPI",
    )
    return solicitacao, analyze_resume(solicitacao)


def test_extracts_texto_do_formato_nativo_gemini() -> None:
    resposta = envelope_gemini('{"resumo_analise":"ok"}')

    assert extract_gemini_text(resposta) == '{"resumo_analise":"ok"}'


def test_gemini_parseia_json_estruturado_com_fences(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.resposta = RespostaHTTPFake(
        200, envelope_gemini("```json\n" + json.dumps(resposta_estruturada()) + "\n```")
    )
    solicitacao, resultado = base_local()

    analise = asyncio.run(provider().gerar_analise_estruturada(solicitacao, resultado))

    assert analise.confianca == 85
    chamada = ClienteHTTPFake.ultima_chamada
    assert chamada["params"] == {"key": "chave-ficticia-para-teste"}
    assert "response_format" not in chamada["json"]
    assert chamada["json"]["generationConfig"] == {"temperature": 0.2}


@pytest.mark.parametrize(
    "status,categoria",
    [(429, "rate_limit_429"), (413, "request_too_large")],
)
def test_gemini_classifica_erros_http(monkeypatch, status, categoria) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.resposta = RespostaHTTPFake(
        status, {"error": {"status": "simulado"}}
    )
    solicitacao, resultado = base_local()

    with pytest.raises(AIProviderError) as capturado:
        asyncio.run(provider().gerar_analise_estruturada(solicitacao, resultado))

    assert capturado.value.categoria == categoria
    assert capturado.value.status_http == status


def test_fluxo_completo_gemini_valido_nao_usa_fallback(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    monkeypatch.setenv("IA_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    ClienteHTTPFake.resposta = RespostaHTTPFake(
        200, envelope_gemini(json.dumps(resposta_estruturada()))
    )
    solicitacao, _ = base_local()

    resultado = asyncio.run(run_analysis_with_fallback(solicitacao))

    assert resultado.fallback_local_usado is False
    assert resultado.provedor_ia == "gemini"
    assert resultado.modelo_ia == "gemini-2.5-flash"
    assert resultado.analise_ia is not None


def test_fluxo_completo_gemini_falha_e_preserva_fallback(monkeypatch) -> None:
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    monkeypatch.setenv("IA_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    ClienteHTTPFake.resposta = RespostaHTTPFake(429, {"error": {}})
    solicitacao, local = base_local()

    resultado = asyncio.run(run_analysis_with_fallback(solicitacao))

    assert resultado.fallback_local_usado is True
    assert resultado.pontuacao_ats == local.pontuacao_ats
    assert resultado.detalhes_erros_provedores[0].categoria_erro == "rate_limit_429"


@pytest.mark.parametrize(
    "texto,categoria",
    [
        ("não-json", "invalid_json"),
        ('{"titulo":"Backend"', "json_truncated"),
        ("", "empty_response"),
        ('{"confianca": 999}', "schema_validation_error"),
    ],
)
def test_tarefa_gemini_classifica_respostas_invalidas(monkeypatch, texto, categoria):
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.resposta = RespostaHTTPFake(200, envelope_gemini(texto))
    with pytest.raises(AIProviderError) as capturado:
        asyncio.run(provider().executar_tarefa_estruturada(
            "classificacao_vaga", "prompt curto", AIJobClassification, 0.1
        ))
    assert capturado.value.categoria == categoria


def test_tarefa_gemini_valida_schema(monkeypatch):
    monkeypatch.setattr("app.providers.gemini.httpx.AsyncClient", ClienteHTTPFake)
    ClienteHTTPFake.resposta = RespostaHTTPFake(200, envelope_gemini(json.dumps({
        "titulo": "Backend", "senioridade": "junior", "requisitos_centrais": ["Python"], "confianca": 90
    })))
    resposta = asyncio.run(provider().executar_tarefa_estruturada(
        "classificacao_vaga", "prompt curto", AIJobClassification, 0.1
    ))
    assert resposta["titulo"] == "Backend" and resposta["confianca"] == 90
