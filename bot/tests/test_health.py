"""Tests for the application's public endpoints."""

import asyncio

from app.main import app
from httpx import ASGITransport, AsyncClient


async def request_app(method: str, path: str, **parameters):
    """Call the ASGI application without an external server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **parameters)


def test_health_behavior_01() -> None:

    # Implementation note.
    response = asyncio.run(request_app("GET", "/health"))

    assert response.status_code == 200

    assert response.json() == {"status": "online"}


def test_legacy_analyze_endpoint_accepts_portuguese_payload(monkeypatch) -> None:

    # Implementation note.
    monkeypatch.setenv("IA_PROVIDER", "mock")

    response = asyncio.run(
        request_app(
            "POST",
            "/api/v1/analisar",
            json={
                "curriculo_texto": "Experiência com Python. Formação em Sistemas. Projetos, habilidades e tecnologias: FastAPI.",
                "vaga_texto": "Buscamos pessoa com Python e FastAPI.",
                "idioma": "pt-BR",
                "usar_ia": True,
                "nivel_vaga": "junior",
                "fontes_curriculo": [],
            },
        )
    )

    assert response.status_code == 200

    result = response.json()

    # Implementation note.
    assert result["pontuacao_ats"] > 0

    assert "Python" in result["palavras_chave_encontradas"]

    # ceonferir mock
    assert result["provedor_ia"] == "mock"

    assert result["modelo_ia"] == "modelo-mock"

    # Technical note removed during English standardization.
    assert result["privacy"]["ai_text_was_sanitized"] is True

    assert result["ai_fallback"]["attempted_providers"] == ["mock"]

    assert "detailed_analysis" in result

    assert "detailed_suggestions" in result


def test_analyze_endpoint_accepts_english_payload(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "mock")
    response = asyncio.run(request_app("POST", "/api/v1/analyze", json={
        "resume_text": "Python and FastAPI project experience.",
        "job_text": "Python and FastAPI are required.",
        "language": "en-US",
        "job_level": "junior",
        "resume_sources": [],
        "use_ai": True,
    }))
    assert response.status_code == 200
    result = response.json()
    assert result["ats_score"] > 0
    assert result["ai_provider"] == "mock"


def test_health_behavior_04(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "mock")
    resume = """HABILIDADES
Python, JavaScript, TypeScript, React, FastAPI, SQL, Docker, Git e testes automatizados.
PROJETOS
API REST em Python e FastAPI com SQL, Docker, Git e testes automatizados.
"""
    job = """Getronics
Requisitos: Angular, React, HTML5, CSS3, JavaScript, TypeScript, APIs REST, Java, Spring Boot, Python, FastAPI, Flask, MVC, SQL e Docker.
Desejáveis: Kubernetes, CI/CD, Git, branches, pull requests, code review, testes unitários, testes de integração, metodologias ágeis, inglês técnico, LLMs e Prompt Engineering.
"""

    response = asyncio.run(
        request_app(
            "POST",
            "/api/v1/analisar",
            json={"curriculo_texto": resume, "vaga_texto": job},
        )
    )

    assert response.status_code == 200
    result = response.json()
    assert "processos" in result["resume_inventory"]
    assert "metodologias ágeis" in result["palavras_chave_faltando"]
    assert "pontuacao_ats" in result
    assert "provedor_ia" in result
