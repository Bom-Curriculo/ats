"""Testes dos endpoints públicos da aplicação."""

import asyncio

from app.main import app
from httpx import ASGITransport, AsyncClient


async def requisitar(metodo: str, caminho: str, **parametros):
    """Chama a aplicação ASGI sem depender de um servidor externo."""

    # usa transport asgi pra não precisar subir servidor de vdd
    transporte = ASGITransport(app=app)

    async with AsyncClient(transport=transporte, base_url="http://teste") as cliente:
        return await cliente.request(metodo, caminho, **parametros)


def test_health_informa_que_servico_esta_online() -> None:

    # olhar se tá no ar
    resposta = asyncio.run(requisitar("GET", "/health"))

    assert resposta.status_code == 200

    assert resposta.json() == {"status": "online"}


def test_endpoint_analisar_respeita_contrato(monkeypatch) -> None:

    # forca provider mock pra não bater em api externa
    monkeypatch.setenv("IA_PROVIDER", "mock")

    resposta = asyncio.run(
        requisitar(
            "POST",
            "/api/v1/analisar",
            json={
                "curriculo_texto": "Experiência com Python. Formação em Sistemas. Projetos, habilidades e tecnologias: FastAPI.",
                "vaga_texto": "Buscamos pessoa com Python e FastAPI.",
                "idioma": "pt-BR",
            },
        )
    )

    assert resposta.status_code == 200

    resultado = resposta.json()

    # score tem que ser positivo pq não tem match
    assert resultado["pontuacao_ats"] > 0

    assert "Python" in resultado["palavras_chave_encontradas"]

    # ceonferir mock
    assert resultado["provedor_ia"] == "mock"

    assert resultado["modelo_ia"] == "modelo-mock"

    # privacidade tem q ta true pois antes de mandar pra IA
    assert resultado["privacidade"]["texto_enviado_para_ia_foi_sanitizado"] is True

    assert resultado["fallback_ia"]["provedores_tentados"] == ["mock"]

    assert "analise_detalhada" in resultado

    assert "sugestoes_detalhadas" in resultado


def test_endpoint_getronics_com_categoria_processos_retorna_200(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "mock")
    curriculo = """HABILIDADES
Python, JavaScript, TypeScript, React, FastAPI, SQL, Docker, Git e testes automatizados.
PROJETOS
API REST em Python e FastAPI com SQL, Docker, Git e testes automatizados.
"""
    vaga = """Getronics
Requisitos: Angular, React, HTML5, CSS3, JavaScript, TypeScript, APIs REST, Java, Spring Boot, Python, FastAPI, Flask, MVC, SQL e Docker.
Desejáveis: Kubernetes, CI/CD, Git, branches, pull requests, code review, testes unitários, testes de integração, metodologias ágeis, inglês técnico, LLMs e Prompt Engineering.
"""

    resposta = asyncio.run(
        requisitar(
            "POST",
            "/api/v1/analisar",
            json={"curriculo_texto": curriculo, "vaga_texto": vaga},
        )
    )

    assert resposta.status_code == 200
    resultado = resposta.json()
    assert "processos" in resultado["inventario_curriculo"]
    assert "metodologias ágeis" in resultado["palavras_chave_faltando"]
    assert "pontuacao_ats" in resultado
    assert "provedor_ia" in resultado
