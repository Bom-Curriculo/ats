"""Tests for the application's public endpoints."""

import asyncio

from dependency_injector import providers
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.resume_analysis import ResumeAnalysisResult


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
    async def extract_resume(self, resume_text: str) -> ResumeAnalysisResult:
        return ResumeAnalysisResult(score=80, suggestion="Adicione métricas de impacto.")


def test_analyze_endpoint_returns_structured_result() -> None:
    app.container.resume_analysis_manager.override(providers.Object(FakeResumeAnalysisManager()))
    try:
        response = asyncio.run(
            request_app(
                "POST",
                "/api/v1/analyze",
                json={"resume_text": "Python and FastAPI project experience."},
            )
        )
    finally:
        app.container.resume_analysis_manager.reset_override()

    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 80
    assert result["suggestion"] == "Adicione métricas de impacto."


def test_analyze_endpoint_rejects_empty_resume_text() -> None:
    response = asyncio.run(request_app("POST", "/api/v1/analyze", json={"resume_text": ""}))

    assert response.status_code == 422
