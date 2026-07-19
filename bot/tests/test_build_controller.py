"""Tests for POST /api/v1/build — reconstructing the best possible ATS resume."""

import asyncio

from dependency_injector import providers
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.resume_analysis import BuiltResumeResult, ProjectItem, ResumeHeader


async def request_app(method: str, path: str, **parameters):
    """Call the ASGI application without an external server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **parameters)


BASE_RESUME_TEXT = (
    "Desenvolvedor backend com experiência em Python, FastAPI e SQL. Atuou em "
    "projetos de automação de currículos, integração com filas de mensagens e "
    "construção de APIs REST para times de produto. Formação em Ciência da "
    "Computação e experiência prévia como estagiário de TI."
)


class FakeResumeAnalysisManager:
    async def build_resume(self, resume_text: str, **_kwargs) -> BuiltResumeResult:
        return BuiltResumeResult(
            score=90,
            professional_summary="Desenvolvedor backend com foco em Python e APIs REST.",
            header=ResumeHeader(name="João Silva"),
            projects=[
                ProjectItem(
                    title="Sistema de Tarefas",
                    start="2024-01",
                    end="2024-06",
                    technologies="Python, Flask",
                )
            ],
        )


def test_build_endpoint_returns_built_resume() -> None:
    app.container.resume_analysis_manager.override(providers.Object(FakeResumeAnalysisManager()))
    try:
        response = asyncio.run(
            request_app("POST", "/api/v1/build", json={"resume_text": BASE_RESUME_TEXT})
        )
    finally:
        app.container.resume_analysis_manager.reset_override()

    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 90
    assert "suggestion" not in result
    assert result["header"]["name"] == "João Silva"
    assert result["projects"] == [
        {
            "title": "Sistema de Tarefas",
            "start": "2024-01",
            "end": "2024-06",
            "technologies": "Python, Flask",
            "description": None,
            "url": None,
        }
    ]


def test_build_endpoint_rejects_missing_resume_source() -> None:
    response = asyncio.run(
        request_app("POST", "/api/v1/build", json={"github_url": "https://github.com/foo"})
    )

    assert response.status_code == 422


class SpyResumeAnalysisManager:
    """Captures every argument build_resume was called with, for assertion."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def build_resume(self, resume_text: str, **kwargs) -> BuiltResumeResult:
        self.calls.append({"resume_text": resume_text, **kwargs})
        return BuiltResumeResult(score=90)


def test_build_endpoint_forwards_every_supporting_source() -> None:
    spy = SpyResumeAnalysisManager()
    app.container.resume_analysis_manager.override(providers.Object(spy))
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/build",
                json={
                    "resume_text": BASE_RESUME_TEXT,
                    "github_url": "https://github.com/pedroaruana",
                    "portfolio_url": "https://pedroaruana.dev",
                    "additional_skills": [{"name": "React", "years": 2}],
                },
            )
        )
    finally:
        app.container.resume_analysis_manager.reset_override()

    assert response.status_code == 200
    call = spy.calls[0]
    assert call["resume_text"] == BASE_RESUME_TEXT
    assert call["github_url"] == "https://github.com/pedroaruana"
    assert call["portfolio_url"] == "https://pedroaruana.dev"
    assert [(skill.name, skill.years) for skill in call["additional_skills"]] == [("React", 2)]
