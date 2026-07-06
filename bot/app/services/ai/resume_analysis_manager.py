from collections.abc import Callable

from app.core.settings import Settings
from app.models.resume_analysis import ResumeAnalysisResult
from app.providers.base import AIProvider, AIProviderError
from app.providers.factory import ProviderFactory, SUPPORTED_PROVIDERS
from app.providers.interfaces import ProviderFactoryInterface
from app.services.ai.interfaces import ResumeAnalysisManagerInterface
from app.services.ai.resume_extraction_prompt import build_resume_extraction_prompt

_ERROR_MESSAGES = {
    "missing_api_key": "{label} has no minimal configuration.",
    "auth_error_401": "{label} rejected the authentication.",
    "permission_error_403": "{label} rejected the requested permission.",
    "rate_limit_429": "{label} reached the request rate limit.",
    "timeout": "{label} exceeded the time limit.",
    "network_error": "Could not connect to {label}.",
    "invalid_model": "{label} did not recognize or did not make available the configured model.",
    "invalid_request": "{label} rejected the request format.",
    "request_too_large": "{label} rejected the request for exceeding the allowed size.",
    "invalid_json": "{label} returned invalid or empty JSON.",
    "json_truncated": "{label} returned apparently truncated JSON.",
    "empty_response": "{label} returned an empty response.",
    "schema_validation_error": "{label} returned data outside the expected schema.",
    "provider_unavailable": "{label} is temporarily unavailable.",
    "unknown_provider_error": "{label} returned an unclassified error.",
}


class ResumeAnalysisManager(ResumeAnalysisManagerInterface):
    """Selects, calls, and safely falls back across configured AI providers."""

    def __init__(
        self,
        settings: Settings | None = None,
        provider_factory: ProviderFactoryInterface | None = None,
    ) -> None:
        self._settings = settings or Settings.load()
        self._provider_factory = provider_factory or ProviderFactory(self._settings)

    def get_provider_chain(self) -> list[str]:
        selected = self._settings.ai.provider
        if selected != "auto":
            if selected not in SUPPORTED_PROVIDERS and selected != "mock":
                raise AIProviderError(f"Unrecognized provider '{selected}'.")
            return [selected]
        chain = list(dict.fromkeys(self._settings.ai.provider_chain))
        invalid = [item for item in chain if item not in SUPPORTED_PROVIDERS and item != "mock"]
        if invalid:
            raise AIProviderError("The provider chain contains an unrecognized provider.")
        if not chain:
            raise AIProviderError("The provider chain has no valid providers.")
        return chain

    def is_provider_configured(self, name: str) -> bool:
        return self._provider_factory.is_configured(name)

    def _safe_error(self, name: str, error: Exception) -> AIProviderError:
        label = name.capitalize()
        category = getattr(error, "category", "unknown_provider_error")
        status = getattr(error, "status_http", None)
        template = _ERROR_MESSAGES.get(category, _ERROR_MESSAGES["unknown_provider_error"])
        return AIProviderError(template.format(label=label), category=category, status_http=status)

    async def extract_resume(
        self, resume_text: str, factory: Callable[[str], AIProvider] | None = None
    ) -> ResumeAnalysisResult:
        """Try each configured provider in order, returning the first successful extraction."""

        factory = factory or self._provider_factory.create
        prompt = build_resume_extraction_prompt(resume_text, self._settings.ai.output_language)
        last_error: AIProviderError | None = None

        for name in self.get_provider_chain():
            if not self.is_provider_configured(name):
                continue

            try:
                provider = factory(name)
                result = await provider.run_structured(prompt, ResumeAnalysisResult, temperature=0.2)
            except Exception as error:
                last_error = self._safe_error(name, error)
                continue

            if isinstance(result, ResumeAnalysisResult):
                return result
            last_error = AIProviderError(
                f"{name.capitalize()} returned data outside the expected schema.",
                category="schema_validation_error",
            )

        raise last_error or AIProviderError(
            "No AI provider is configured.", category="missing_api_key"
        )
