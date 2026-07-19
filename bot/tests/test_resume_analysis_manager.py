import asyncio

import pytest

from app.models.resume_analysis import BuiltResumeResult, ResumeHeader, ResumeScoreResult, SkillItem
from app.providers.base import AIProviderError
from app.providers.mock import MockProvider
from app.services.ai.resume_analysis_manager import ResumeAnalysisManager

RESUME_TEXT = "COMPETÊNCIAS\nPython, FastAPI, SQL."


def make_score(score: int = 70) -> ResumeScoreResult:
    return ResumeScoreResult(score=score, suggestion="Adicione métricas de impacto.")


def make_built(score: int = 70) -> BuiltResumeResult:
    return BuiltResumeResult(score=score)


class ProviderFake(MockProvider):
    def __init__(self, name: str, should_fail: bool = False, prompts: list | None = None):
        super().__init__(model=f"modelo-{name}", structured_response=make_built())
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
        ResumeAnalysisManager().build_resume(
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
        ResumeAnalysisManager().build_resume(
            RESUME_TEXT, lambda name: ProviderFake(name, should_fail=name == "groq")
        )
    )

    assert isinstance(result, BuiltResumeResult)


def test_skips_providers_without_configuration(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")
    calls = []

    result = asyncio.run(
        ResumeAnalysisManager().build_resume(
            RESUME_TEXT, lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == ["gemini"]
    assert isinstance(result, BuiltResumeResult)


def test_raises_when_every_provider_fails(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    with pytest.raises(AIProviderError):
        asyncio.run(
            ResumeAnalysisManager().build_resume(
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

    result = asyncio.run(ResumeAnalysisManager().build_resume(RESUME_TEXT, factory))

    assert calls == ["groq", "gemini"]
    assert isinstance(result, BuiltResumeResult)


@pytest.mark.parametrize("selected,forbidden", [("groq", "deepseek"), ("deepseek", "groq")])
def test_pinned_provider_never_calls_others(monkeypatch, selected, forbidden) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", selected)
    calls = []

    asyncio.run(
        ResumeAnalysisManager().build_resume(
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
            ResumeAnalysisManager().build_resume(RESUME_TEXT, lambda name: FailingProvider(name))
        )

    assert captured.value.category == category
    assert captured.value.status_http == status
    assert "detail interno" not in str(captured.value)


def test_merges_github_and_portfolio_into_header_links_regardless_of_ai_output(monkeypatch) -> None:
    """Known-exact values must land correctly even if the AI ignores/misplaces them."""
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    ai_result = BuiltResumeResult(score=70, header=ResumeHeader(links={"Other": "https://example.com"}))

    result = asyncio.run(
        ResumeAnalysisManager().build_resume(
            RESUME_TEXT,
            lambda name: MockProvider(structured_response=ai_result),
            github_url="https://github.com/pedroaruana",
            portfolio_url="https://pedroaruana.dev",
        )
    )

    assert result.header.links["GitHub"] == "https://github.com/pedroaruana"
    assert result.header.links["Portfolio"] == "https://pedroaruana.dev"
    assert result.header.links["Other"] == "https://example.com"


def test_merges_additional_skills_without_duplicating_existing_ones(monkeypatch) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    ai_result = BuiltResumeResult(
        score=70, skills=[SkillItem(name="Python"), SkillItem(name="docker")]
    )

    result = asyncio.run(
        ResumeAnalysisManager().build_resume(
            RESUME_TEXT,
            lambda name: MockProvider(structured_response=ai_result),
            additional_skills=[SkillItem(name="Docker", years=3), SkillItem(name="GraphQL", years=1)],
        )
    )

    names = sorted(skill.name.lower() for skill in result.skills)
    assert names == ["docker", "graphql", "python"]


def test_additional_skill_years_overrides_ai_guess_for_an_existing_skill(monkeypatch) -> None:
    """Laravel sends name + years per skill (e.g. PHP -> 5 anos); the user's own number wins."""
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    ai_result = BuiltResumeResult(score=70, skills=[SkillItem(name="PHP", years=2)])

    result = asyncio.run(
        ResumeAnalysisManager().build_resume(
            RESUME_TEXT,
            lambda name: MockProvider(structured_response=ai_result),
            additional_skills=[SkillItem(name="PHP", years=5)],
        )
    )

    php_skills = [skill for skill in result.skills if skill.name.lower() == "php"]
    assert len(php_skills) == 1
    assert php_skills[0].years == 5


def test_score_resume_uses_first_configured_provider_in_chain(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    calls = []

    def factory(name):
        calls.append(name)
        return MockProvider(structured_response=make_score(85))

    result = asyncio.run(ResumeAnalysisManager().score_resume(RESUME_TEXT, factory))

    assert calls == ["groq"]
    assert isinstance(result, ResumeScoreResult)
    assert result.score == 85


def test_score_resume_falls_back_to_next_provider_on_failure(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    def factory(name):
        if name == "groq":
            return MockProvider(simulated_error=AIProviderError("boom"))
        return MockProvider(structured_response=make_score())

    result = asyncio.run(ResumeAnalysisManager().score_resume(RESUME_TEXT, factory))

    assert isinstance(result, ResumeScoreResult)
