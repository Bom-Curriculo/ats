from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel

from app.core.settings import Settings
from app.models.resume_analysis import BuiltResumeResult, ResumeScoreResult, SkillItem
from app.providers.base import AIProvider, AIProviderError
from app.providers.factory import ProviderFactory, SUPPORTED_PROVIDERS
from app.providers.interfaces import ProviderFactoryInterface
from app.services.ai.interfaces import ResumeAnalysisManagerInterface
from app.services.ai.resume_builder_prompt import build_resume_construction_prompt
from app.services.ai.resume_score_prompt import build_resume_score_prompt

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

_SchemaT = TypeVar("_SchemaT", bound=BaseModel)


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

    async def score_resume(
        self,
        resume_text: str,
        factory: Callable[[str], AIProvider] | None = None,
        linkedin_text: str | None = None,
        github_url: str | None = None,
        portfolio_url: str | None = None,
        additional_skills: list[SkillItem] | None = None,
    ) -> ResumeScoreResult:
        """Judge the resume exactly as given: a 0-100 ATS score plus one improvement suggestion."""

        prompt = build_resume_score_prompt(
            resume_text,
            self._settings.ai.output_language,
            linkedin_text=linkedin_text,
            github_url=github_url,
            portfolio_url=portfolio_url,
            additional_skills=additional_skills,
        )
        return await self._run_with_fallback(prompt, ResumeScoreResult, factory)

    async def build_resume(
        self,
        resume_text: str,
        factory: Callable[[str], AIProvider] | None = None,
        linkedin_text: str | None = None,
        github_url: str | None = None,
        portfolio_url: str | None = None,
        additional_skills: list[SkillItem] | None = None,
    ) -> BuiltResumeResult:
        """Reconstruct the best possible ATS-optimized resume from every given source.

        ``linkedin_text``/``github_url``/``portfolio_url``/``additional_skills`` are
        optional supporting sources folded into the same prompt as the base resume,
        so the AI produces one coherent result instead of the caller merging several.
        """

        prompt = build_resume_construction_prompt(
            resume_text,
            self._settings.ai.output_language,
            linkedin_text=linkedin_text,
            github_url=github_url,
            portfolio_url=portfolio_url,
            additional_skills=additional_skills,
        )
        result = await self._run_with_fallback(prompt, BuiltResumeResult, factory)
        return self._merge_known_facts(result, github_url, portfolio_url, additional_skills)

    async def _run_with_fallback(
        self,
        prompt: str,
        schema: type[_SchemaT],
        factory: Callable[[str], AIProvider] | None,
    ) -> _SchemaT:
        factory = factory or self._provider_factory.create
        last_error: AIProviderError | None = None

        for name in self.get_provider_chain():
            if not self.is_provider_configured(name):
                continue

            try:
                provider = factory(name)
                result = await provider.run_structured(prompt, schema, temperature=0.2)
            except Exception as error:
                last_error = self._safe_error(name, error)
                continue

            if isinstance(result, schema):
                return result
            last_error = AIProviderError(
                f"{name.capitalize()} returned data outside the expected schema.",
                category="schema_validation_error",
            )

        raise last_error or AIProviderError(
            "No AI provider is configured.", category="missing_api_key"
        )

    def _merge_known_facts(
        self,
        result: BuiltResumeResult,
        github_url: str | None,
        portfolio_url: str | None,
        additional_skills: list[SkillItem] | None,
    ) -> BuiltResumeResult:
        """Force in values we already know exactly, regardless of what the AI did with them.

        The prompt already asks the AI to place these, but instruction-following isn't
        guaranteed — GitHub/portfolio links and user-typed skills are known facts, not
        something that needs to be inferred, so they must never depend on the AI
        transcribing them correctly.
        """

        if github_url:
            result.header.links["GitHub"] = github_url
        if portfolio_url:
            result.header.links["Portfolio"] = portfolio_url
        if additional_skills:
            by_name = {skill.name.strip().lower(): skill for skill in result.skills}
            for reported in additional_skills:
                key = reported.name.strip().lower()
                existing = by_name.get(key)
                if existing is not None:
                    # The user's own reported years take precedence over the AI's guess.
                    if reported.years is not None:
                        existing.years = reported.years
                else:
                    new_skill = SkillItem(name=reported.name, years=reported.years)
                    result.skills.append(new_skill)
                    by_name[key] = new_skill
        return result
