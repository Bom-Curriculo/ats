"""Tests for the application's public endpoints."""

import asyncio

from dependency_injector import providers
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.resume_analysis import ResumeScoreResult


async def request_app(method: str, path: str, **parameters):
    """Call the ASGI application without an external server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **parameters)


def test_health_behavior_01() -> None:
    response = asyncio.run(request_app("GET", "/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "online"}


class FakeResumeAnalysisManager:
    async def score_resume(self, resume_text: str, **_kwargs) -> ResumeScoreResult:
        return ResumeScoreResult(score=80, suggestion="Adicione métricas de impacto.")


def test_analyze_endpoint_returns_score_and_suggestion() -> None:
    app.container.resume_analysis_manager.override(providers.Object(FakeResumeAnalysisManager()))
    resume_text = (
        "Desenvolvedor backend com experiência em Python, FastAPI e SQL. "
        "Atuou em projetos de automação de currículos, integração com filas de "
        "mensagens e construção de APIs REST para times de produto. Formação em "
        "Ciência da Computação e experiência prévia como estagiário de TI."
    )
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/analyze",
                json={"resume_text": resume_text},
            )
        )
    finally:
        app.container.resume_analysis_manager.reset_override()

    assert response.status_code == 200
    assert response.json() == {"score": 80, "suggestion": "Adicione métricas de impacto."}


def test_analyze_endpoint_rejects_empty_resume_text() -> None:
    response = asyncio.run(request_app("POST", "/api/v1/analyze", json={"resume_text": ""}))

    assert response.status_code == 422


def test_analyze_endpoint_rejects_missing_resume_source() -> None:
    """Neither resume_text nor resume_cv_url given: 422, not a 500."""
    response = asyncio.run(
        request_app("POST", "/api/v1/analyze", json={"github_url": "https://github.com/foo"})
    )

    assert response.status_code == 422


BASE_RESUME_TEXT = (
    "Desenvolvedor backend com experiência em Python, FastAPI e SQL. Atuou em "
    "projetos de automação de currículos, integração com filas de mensagens e "
    "construção de APIs REST para times de produto. Formação em Ciência da "
    "Computação e experiência prévia como estagiário de TI."
)


class SpyResumeAnalysisManager:
    """Captures every argument score_resume was called with, for assertion."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def score_resume(self, resume_text: str, **kwargs) -> ResumeScoreResult:
        self.calls.append({"resume_text": resume_text, **kwargs})
        return ResumeScoreResult(score=80, suggestion="Adicione métricas de impacto.")


def test_analyze_endpoint_forwards_every_supporting_source() -> None:
    spy = SpyResumeAnalysisManager()
    app.container.resume_analysis_manager.override(providers.Object(spy))
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/analyze",
                json={
                    "resume_text": BASE_RESUME_TEXT,
                    "github_url": "https://github.com/pedroaruana",
                    "portfolio_url": "https://pedroaruana.dev",
                    "additional_skills": [{"name": "React", "years": 2}, {"name": "Docker"}],
                },
            )
        )
    finally:
        app.container.resume_analysis_manager.reset_override()

    assert response.status_code == 200
    assert len(spy.calls) == 1
    call = spy.calls[0]
    assert call["resume_text"] == BASE_RESUME_TEXT
    assert call["github_url"] == "https://github.com/pedroaruana"
    assert call["portfolio_url"] == "https://pedroaruana.dev"
    assert [(skill.name, skill.years) for skill in call["additional_skills"]] == [
        ("React", 2),
        ("Docker", None),
    ]


class FakeResumeFileFetcher:
    def __init__(self, text_by_url: dict[str, str]) -> None:
        self._text_by_url = text_by_url

    async def fetch_and_extract_text(self, url: str) -> str:
        return self._text_by_url[url]


def test_analyze_endpoint_fetches_cv_and_linkedin_from_url() -> None:
    spy = SpyResumeAnalysisManager()
    fetcher = FakeResumeFileFetcher(
        {
            "https://files.example.com/cv.pdf": BASE_RESUME_TEXT,
            "https://files.example.com/linkedin.pdf": "Resumo do LinkedIn com experiência extra.",
        }
    )
    app.container.resume_analysis_manager.override(providers.Object(spy))
    app.container.resume_file_fetcher.override(providers.Object(fetcher))
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/analyze",
                json={
                    "resume_cv_url": "https://files.example.com/cv.pdf",
                    "resume_linkedin_url": "https://files.example.com/linkedin.pdf",
                },
            )
        )
    finally:
        app.container.resume_analysis_manager.reset_override()
        app.container.resume_file_fetcher.reset_override()

    assert response.status_code == 200
    call = spy.calls[0]
    assert call["resume_text"] == BASE_RESUME_TEXT
    assert call["linkedin_text"] == "Resumo do LinkedIn com experiência extra."


def test_analyze_endpoint_returns_422_when_cv_url_cannot_be_fetched() -> None:
    class FailingFetcher:
        async def fetch_and_extract_text(self, url: str) -> str:
            raise RuntimeError("boom")

    app.container.resume_file_fetcher.override(providers.Object(FailingFetcher()))
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/analyze",
                json={"resume_cv_url": "https://files.example.com/cv.pdf"},
            )
        )
    finally:
        app.container.resume_file_fetcher.reset_override()

    assert response.status_code == 422
