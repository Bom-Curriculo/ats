import asyncio

import pytest

from app.providers.base import AIProviderError
from app.providers.factory import ProviderFactory
from app.providers.langchain_provider import LangChainProvider
from app.core.settings import AISettings, ProviderSettings, Settings
from app.models.analysis import AnalysisRequest
from app.models.ai_analysis import AIAnalysisResponse
from app.models.ai_pipeline import AIJobClassification
from app.services.ats_analyzer import analyze_resume


class FakeStructuredRunnable:
    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error

    async def ainvoke(self, prompt):
        if self._error is not None:
            raise self._error
        return self._result


class FakeChatModel:
    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error
        self.bound_kwargs: dict | None = None

    def bind(self, **kwargs):
        self.bound_kwargs = kwargs
        return self

    def with_structured_output(self, schema):
        return FakeStructuredRunnable(self._result, self._error)


def make_provider(result=None, error: Exception | None = None) -> LangChainProvider:
    provider = LangChainProvider(name="gemini", model="gemini-2.5-flash", api_key="fake-key")
    provider._chat_model = FakeChatModel(result=result, error=error)
    return provider


def analysis_response(**overrides) -> AIAnalysisResponse:
    defaults = dict(
        contextual_summary="Compatibility analyzed without inventing experience.",
        contextual_requirements=[],
        strengths=["Python appears in the resume."],
        gaps=["FastAPI does not appear in the resume."],
        possible_blockers=[],
        improvement_suggestions=["Detail real projects."],
        next_steps=["Study FastAPI before claiming experience."],
        anti_fabrication_alerts=["Do not declare missing skills."],
        confidence=85,
    )
    defaults.update(overrides)
    return AIAnalysisResponse(**defaults)


def local_base():
    request = AnalysisRequest(
        resume_text="SKILLS\nPython", job_text="Requirements:\nPython and FastAPI"
    )
    return request, analyze_resume(request)


def test_generate_completion_returns_summary_and_suggestions() -> None:
    provider = make_provider(result=analysis_response())
    request, base_result = local_base()

    complement = asyncio.run(provider.generate_completion(request, base_result))

    assert "Compatibility analyzed" in complement.generated_summary
    assert "Detail real projects." in complement.suggestions
    assert "Study FastAPI before claiming experience." in complement.suggestions


def test_run_structured_task_returns_dumped_schema() -> None:
    classification = AIJobClassification(
        title="Backend", seniority="junior", core_requirements=["Python"], confidence=90
    )
    provider = make_provider(result=classification)

    response = asyncio.run(
        provider.run_structured_task("job_classification", "short prompt", AIJobClassification, 0.1)
    )

    assert response["title"] == "Backend"
    assert response["confidence"] == 90
    assert provider._chat_model.bound_kwargs == {"temperature": 0.1}


def test_empty_structured_response_raises_empty_response_category() -> None:
    provider = make_provider(result=None)

    with pytest.raises(AIProviderError) as captured:
        asyncio.run(provider.run_structured_task("job_classification", "prompt", AIJobClassification))

    assert captured.value.category == "empty_response"


@pytest.mark.parametrize(
    "error_type_name,status_code,expected_category",
    [
        ("RateLimitError", 429, "rate_limit_429"),
        ("AuthenticationError", 401, "auth_error_401"),
        ("PermissionDeniedError", 403, "permission_error_403"),
        ("NotFoundError", 404, "invalid_model"),
        ("BadRequestError", 400, "invalid_request"),
        ("APITimeoutError", None, "timeout"),
        ("APIConnectionError", None, "network_error"),
        ("InternalServerError", 503, "provider_unavailable"),
        ("SomethingUnexpected", None, "unknown_provider_error"),
    ],
)
def test_provider_errors_are_mapped_to_stable_categories(
    error_type_name, status_code, expected_category
) -> None:
    error_type = type(error_type_name, (Exception,), {})
    error = error_type("simulated failure")
    if status_code is not None:
        error.status_code = status_code
    provider = make_provider(error=error)

    with pytest.raises(AIProviderError) as captured:
        asyncio.run(provider.run_structured_task("job_classification", "prompt", AIJobClassification))

    assert captured.value.category == expected_category


def test_provider_requires_api_key_except_for_ollama() -> None:
    with pytest.raises(AIProviderError) as captured:
        LangChainProvider(name="groq", model="some-model", api_key="")
    assert captured.value.category == "missing_api_key"

    LangChainProvider(name="ollama", model="qwen3:8b", base_url="http://localhost:11434")


def _settings_with_providers(**providers: ProviderSettings) -> Settings:
    base = Settings.load()
    return Settings(
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


def test_provider_factory_reports_configuration_state() -> None:
    settings = _settings_with_providers(
        groq=ProviderSettings(model="m", timeout_seconds=1.0, api_key=""),
        ollama=ProviderSettings(model="m", timeout_seconds=1.0, base_url="http://localhost:11434"),
    )
    factory = ProviderFactory(settings)

    assert factory.is_configured("groq") is False
    assert factory.is_configured("ollama") is True
    assert factory.is_configured("mock") is True


def test_provider_factory_creates_mock_and_rejects_unknown_names() -> None:
    settings = _settings_with_providers()
    factory = ProviderFactory(settings)

    assert factory.create("mock").name == "mock"
    with pytest.raises(AIProviderError):
        factory.create("not-a-real-provider")
