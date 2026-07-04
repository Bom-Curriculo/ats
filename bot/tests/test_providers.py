import asyncio
from pathlib import Path

import pytest
from dotenv import dotenv_values
from app.providers.base import AIProviderError
from app.providers.factory import create_provider
from app.providers.mock import MockProvider
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume_with_ai

"""Provider tests that never call external services."""


def test_providers_behavior_01() -> None:

    request = AnalysisRequest(
        resume_text="Experiência com Python.",
        job_text="Python FastAPI",
        use_ai=True,
    )

    provider = MockProvider(
        summary="Resumo controlado.",
        suggestions=["Sugestão controlada."],
    )

    result = asyncio.run(analyze_resume_with_ai(request, provider))

    # Technical note removed during English standardization.
    assert result.ats_score == 50

    assert result.generated_summary == "Resumo controlado."

    assert result.suggestions == ["Sugestão controlada."]

    assert result.ai_provider == "mock"

    assert result.ai_model == "modelo-mock"


def test_groq_without_key_returns_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.setenv("IA_PROVIDER", "groq")

    # Implementation note.
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(AIProviderError, match="GROQ_API_KEY"):
        create_provider()


def test_providers_behavior_03(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.delenv("GROQ_MODEL", raising=False)

    provider = create_provider("groq")

    assert provider.model == "openai/gpt-oss-120b"


def test_providers_behavior_04(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    provider = create_provider("groq")

    assert provider.model == "llama-3.3-70b-versatile"


DEFAULT_MODELS = {
    "groq": ("GROQ_MODEL", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "gemini": ("GEMINI_MODEL", "GEMINI_API_KEY", "gemini-2.5-pro"),
    "deepseek": ("DEEPSEEK_MODEL", "DEEPSEEK_API_KEY", "deepseek-v4-flash"),
    "openai": ("OPENAI_MODEL", "OPENAI_API_KEY", "gpt-5.5"),
    "ollama": ("OLLAMA_MODEL", None, "qwen3:8b"),
}


@pytest.mark.parametrize("name", DEFAULT_MODELS)
def test_providers_behavior_05(monkeypatch, name) -> None:
    model_variable, key_variable, expected = DEFAULT_MODELS[name]
    monkeypatch.delenv(model_variable, raising=False)
    if key_variable:
        monkeypatch.setenv(key_variable, "chave-ficticia-para-teste")

    provider = create_provider(name)
    example = dotenv_values(Path(__file__).parents[1] / ".env.example")

    assert provider.model == expected
    assert example[model_variable] == expected


@pytest.mark.parametrize("name", DEFAULT_MODELS)
def test_providers_behavior_06(monkeypatch, name) -> None:
    model_variable, key_variable, _ = DEFAULT_MODELS[name]
    model_customizado = f"modelo-customizado-{name}"
    monkeypatch.setenv(model_variable, model_customizado)
    if key_variable:
        monkeypatch.setenv(key_variable, "chave-ficticia-para-teste")

    provider = create_provider(name)

    assert provider.model == model_customizado


def test_provider_unknown_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:

    # Implementation note.
    monkeypatch.setenv("IA_PROVIDER", "inexistente")

    with pytest.raises(AIProviderError, match="não reconhecido"):
        create_provider()


def test_providers_behavior_08(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    # Implementation note.
    monkeypatch.delenv("IA_PROVIDER", raising=False)

    with pytest.raises(AIProviderError, match="auto"):
        create_provider()
