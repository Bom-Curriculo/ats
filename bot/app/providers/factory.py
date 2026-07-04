from app.core.settings import Settings
from app.providers.base import AIProvider, AIProviderError
from app.providers.interfaces import ProviderFactoryInterface
from app.providers.langchain_provider import LangChainProvider
from app.providers.mock import MockProvider

SUPPORTED_PROVIDERS = ("groq", "gemini", "deepseek", "openai", "ollama")


class ProviderFactory(ProviderFactoryInterface):
    """Builds configured `AIProvider` instances from `Settings` alone."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self, name: str) -> bool:
        if name == "mock":
            return True
        provider_settings = self._settings.ai.providers.get(name)
        return provider_settings is not None and provider_settings.is_configured()

    def create(self, name: str | None = None) -> AIProvider:
        name = (name or self._settings.ai.provider).strip().lower()
        if name == "mock":
            return MockProvider()
        if name not in SUPPORTED_PROVIDERS:
            raise AIProviderError(
                f"Unrecognized provider '{name}'. Use auto, mock, "
                f"{', '.join(SUPPORTED_PROVIDERS)}."
            )

        provider_settings = self._settings.ai.providers.get(name)
        if provider_settings is None:
            raise AIProviderError(f"Provider '{name}' has no configuration entry.", category="missing_api_key")

        return LangChainProvider(
            name=name,
            model=provider_settings.model,
            api_key=provider_settings.api_key,
            base_url=provider_settings.base_url,
            timeout=provider_settings.timeout_seconds,
            output_language=self._settings.ai.output_language,
        )
