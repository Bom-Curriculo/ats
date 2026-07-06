import asyncio

import pytest

from app.models.resume_analysis import ResumeAnalysisResult
from app.providers.base import AIProviderError
from app.providers.mock import MockProvider
from app.services.ai.resume_analysis_manager import ResumeAnalysisManager

RESUME_TEXT = "COMPETÊNCIAS\nPython, FastAPI, SQL."


def make_result(score: int = 70) -> ResumeAnalysisResult:
    return ResumeAnalysisResult(score=score, suggestion="Adicione métricas de impacto.")


class ProviderFake(MockProvider):
    def __init__(self, name: str, should_fail: bool = False, prompts: list | None = None):
        super().__init__(model=f"modelo-{name}", structured_response=make_result())
        self.name = name
        self.should_fail = should_fail
        self._prompts = prompts

    async def run_structured(self, prompt, schema, temperature=0.2):
        if self._prompts is not None:
            self._prompts.append((self.name, prompt))
        if self.should_fail:
            raise AIProviderError(f"Falha simulada de {self.name}")
        return await super().run_structured(prompt, schema, temperature)


def configure_keys(monkeypatch):
    for name in ("GROQ", "GEMINI", "DEEPSEEK", "OPENAI"):
        monkeypatch.setenv(f"{name}_API_KEY", "chave-ficticia-para-teste")


def test_uses_first_configured_provider_in_chain(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    calls = []

    result = asyncio.run(
        ResumeAnalysisManager().extract_resume(
            RESUME_TEXT, lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == ["groq"]
    assert result.score == 70


def test_falls_back_to_next_provider_on_failure(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    result = asyncio.run(
        ResumeAnalysisManager().extract_resume(
            RESUME_TEXT, lambda name: ProviderFake(name, should_fail=name == "groq")
        )
    )

    assert isinstance(result, ResumeAnalysisResult)


def test_skips_providers_without_configuration(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    calls = []

    result = asyncio.run(
        ResumeAnalysisManager().extract_resume(
            RESUME_TEXT, lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == ["gemini"]
    assert isinstance(result, ResumeAnalysisResult)


def test_raises_when_every_provider_fails(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    with pytest.raises(AIProviderError):
        asyncio.run(
            ResumeAnalysisManager().extract_resume(
                RESUME_TEXT, lambda name: ProviderFake(name, should_fail=True)
            )
        )


def test_invalid_structured_response_tries_next_provider(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    calls = []

    def factory(name):
        calls.append(name)
        if name == "groq":
            return MockProvider(structured_response=None)
        return ProviderFake(name)

    result = asyncio.run(ResumeAnalysisManager().extract_resume(RESUME_TEXT, factory))

    assert calls == ["groq", "gemini"]
    assert isinstance(result, ResumeAnalysisResult)


@pytest.mark.parametrize("selected,forbidden", [("groq", "deepseek"), ("deepseek", "groq")])
def test_pinned_provider_never_calls_others(monkeypatch, selected, forbidden) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", selected)
    calls = []

    asyncio.run(
        ResumeAnalysisManager().extract_resume(
            RESUME_TEXT, lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == [selected]
    assert forbidden not in calls


@pytest.mark.parametrize(
    "category,status",
    [
        ("auth_error_401", 401),
        ("permission_error_403", 403),
        ("rate_limit_429", 429),
        ("timeout", None),
    ],
)
def test_provider_failure_is_sanitized(monkeypatch, category, status) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    class FailingProvider(ProviderFake):
        async def run_structured(self, prompt, schema, temperature=0.2):
            raise AIProviderError("detail interno que não deve sair", category=category, status_http=status)

    with pytest.raises(AIProviderError) as captured:
        asyncio.run(
            ResumeAnalysisManager().extract_resume(RESUME_TEXT, lambda name: FailingProvider(name))
        )

    assert captured.value.category == category
    assert captured.value.status_http == status
    assert "detail interno" not in str(captured.value)
