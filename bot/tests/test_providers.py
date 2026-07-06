import pytest

from app.core.settings import AISettings, ProviderSettings, Settings
from app.providers.base import AIProviderError
from app.providers.factory import ProviderFactory

"""Provider tests that never call external services."""


def _factory(**providers: ProviderSettings) -> ProviderFactory:
    base = Settings.load()
    settings = Settings(
        server=base.server,
        ai=AISettings(
            enabled_by_default=True,
            output_language="pt-BR",
            provider="auto",
            provider_chain=tuple(providers.keys()),
            providers=providers,
        ),
        rabbitmq=base.rabbitmq,
    )
    return ProviderFactory(settings)


def test_groq_without_key_returns_clear_error() -> None:
    factory = _factory(groq=ProviderSettings(model="openai/gpt-oss-120b", timeout_seconds=120.0, api_key=""))

    with pytest.raises(AIProviderError) as captured:
        factory.create("groq")

    assert captured.value.category == "missing_api_key"


def test_provider_uses_configured_default_model() -> None:
    factory = _factory(groq=ProviderSettings(model="openai/gpt-oss-120b", timeout_seconds=120.0, api_key="fake-key"))

    provider = factory.create("groq")

    assert provider.model == "openai/gpt-oss-120b"


def test_provider_uses_custom_configured_model() -> None:
    factory = _factory(groq=ProviderSettings(model="llama-3.3-70b-versatile", timeout_seconds=120.0, api_key="fake-key"))

    provider = factory.create("groq")

    assert provider.model == "llama-3.3-70b-versatile"


CONFIGURED_DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-120b",
    "gemini": "gemini-3.5-flash",
    "deepseek": "deepseek-v4-flash",
    "openai": "gpt-5.5",
    "ollama": "qwen3:8b",
}


@pytest.mark.parametrize("name,expected_model", CONFIGURED_DEFAULT_MODELS.items())
def test_config_yaml_default_models_match_expected(name, expected_model) -> None:
    settings = Settings.load()

    assert settings.ai.providers[name].model == expected_model


def test_provider_unknown_returns_error() -> None:
    factory = _factory()

    with pytest.raises(AIProviderError, match="Unrecognized"):
        factory.create("inexistente")


def test_provider_auto_is_never_directly_creatable() -> None:
    factory = _factory()

    with pytest.raises(AIProviderError, match="auto"):
        factory.create("auto")
