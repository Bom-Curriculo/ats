from collections.abc import Callable

from app.core.settings import Settings
from app.providers.base import AIProviderError, AIProvider
from app.providers.factory import ProviderFactory, SUPPORTED_PROVIDERS
from app.providers.interfaces import ProviderFactoryInterface
from app.models.analysis import (
    AIFallback,
    SanitizedProviderError,
    PrivacyInformation,
    AnalysisResult,
    AnalysisRequest,
)
from app.services.ai.interfaces import AIManagerInterface
from app.services.analysis.interfaces import AtsAnalysisServiceInterface
from app.services.analysis.ats_analysis_service import AtsAnalysisService
from app.services.privacy.interfaces import SanitizerInterface
from app.services.privacy.sanitizer import PrivacySanitizer

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


class AIManager(AIManagerInterface):
    """Selects, calls, and safely falls back across configured AI providers."""

    def __init__(
        self,
        settings: Settings | None = None,
        provider_factory: ProviderFactoryInterface | None = None,
        sanitizer: SanitizerInterface | None = None,
        ats_analysis_service: AtsAnalysisServiceInterface | None = None,
    ) -> None:
        self._settings = settings or Settings.load()
        self._provider_factory = provider_factory or ProviderFactory(self._settings)
        self._sanitizer = sanitizer or PrivacySanitizer()
        self._ats_analysis = ats_analysis_service or AtsAnalysisService()

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

    def _safe_error(self, name: str, model: str | None, error: Exception) -> SanitizedProviderError:
        label = name.capitalize()
        category = getattr(error, "category", "unknown_provider_error")
        status = getattr(error, "status_http", None)
        template = _ERROR_MESSAGES.get(category, _ERROR_MESSAGES["unknown_provider_error"])
        return SanitizedProviderError(
            provider=name,
            model=model,
            error_category=category,
            status_http=status,
            safe_message=template.format(label=label),
        )

    def _is_ai_enabled(self, request: AnalysisRequest) -> bool:
        """An explicit request option overrides the configured default."""
        if request.use_ai is not None:
            return request.use_ai
        return self._settings.ai.enabled_by_default

    async def run_analysis_with_fallback(
        self,
        request: AnalysisRequest,
        factory: Callable[[str], AIProvider] | None = None,
    ) -> AnalysisResult:
        """Run local analysis and safely apply optional AI enrichment."""

        factory = factory or self._provider_factory.create

        result = self._ats_analysis.analyze(request)
        resume = self._sanitizer.sanitize(request.resume_text)
        job = self._sanitizer.sanitize(request.job_text)
        removed_items = list(dict.fromkeys(resume.items_removed + job.items_removed))
        safe_request = request.model_copy(
            update={
                "resume_text": resume.text_sanitized,
                "job_text": job.text_sanitized,
                "resume_sources": [],
            }
        )
        if not self._is_ai_enabled(request):
            return result.model_copy(
                update={
                    "local_fallback_used": True,
                    "privacy": PrivacyInformation(
                        sensitive_data_detected=bool(removed_items),
                        items_removed_before_ai=removed_items,
                        ai_text_was_sanitized=False,
                    ),
                }
            )

        chain = self.get_provider_chain()
        attempted: list[str] = []
        skipped: list[str] = []
        last_error: str | None = None
        errors: list[str] = []
        error_details: list[SanitizedProviderError] = []

        for index, name in enumerate(chain):
            if not self.is_provider_configured(name):
                skipped.append(name)
                continue

            attempted.append(name)
            provider: AIProvider | None = None
            try:
                provider = factory(name)
                enriched = await self._ats_analysis.analyze_with_ai(safe_request, provider, propagate_provider_error=True)

                if enriched.local_fallback_used or enriched.ai_analysis is None:
                    last_error = f"{name.capitalize()} returned an empty, invalid, or validation-rejected response."
                    errors.append(last_error)
                    error_details.append(
                        SanitizedProviderError(
                            provider=name,
                            model=provider.model,
                            error_category="schema_validation_error",
                            safe_message=last_error,
                        )
                    )
                    continue

                fallback = AIFallback(
                    fallback_used=index > 0 or len(attempted) > 1,
                    attempted_providers=attempted,
                    providers_skipped_by_configuration=skipped,
                    last_sanitized_error=last_error,
                    sanitized_provider_errors=errors,
                )

                return enriched.model_copy(
                    update={
                        "ai_fallback": fallback,
                        "attempted_providers": attempted,
                        "sanitized_provider_errors": errors,
                        "provider_error_details": error_details,
                        "privacy": PrivacyInformation(
                            sensitive_data_detected=bool(removed_items),
                            items_removed_before_ai=removed_items,
                            ai_text_was_sanitized=True,
                        ),
                    }
                )

            except Exception as error:
                detail = self._safe_error(name, getattr(provider, "model", None), error)
                last_error = detail.safe_message
                errors.append(last_error)
                error_details.append(detail)

        fallback = AIFallback(
            fallback_used=True,
            attempted_providers=attempted,
            providers_skipped_by_configuration=skipped,
            last_sanitized_error=last_error,
            sanitized_provider_errors=errors,
        )

        return result.model_copy(
            update={
                "local_fallback_used": True,
                "ai_provider": "sem_ia",
                "ai_model": None,
                "ai_fallback": fallback,
                "attempted_providers": attempted,
                "sanitized_provider_errors": errors,
                "provider_error_details": error_details,
                "privacy": PrivacyInformation(
                    sensitive_data_detected=bool(removed_items),
                    items_removed_before_ai=removed_items,
                    ai_text_was_sanitized=bool(attempted),
                ),
            }
        )
