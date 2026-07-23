import asyncio

import pytest

from app.models.resume_analysis import BuiltResumeResult
from app.providers.base import AIProviderError
from app.providers.langchain_provider import LangChainProvider


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


def test_run_structured_returns_the_parsed_model() -> None:
    expected = BuiltResumeResult(score=80)
    provider = make_provider(result=expected)

    response = asyncio.run(provider.run_structured("short prompt", BuiltResumeResult, 0.1))

    assert response is expected
    assert provider._chat_model.bound_kwargs == {"temperature": 0.1}


def test_empty_structured_response_raises_empty_response_category() -> None:
    provider = make_provider(result=None)

    with pytest.raises(AIProviderError) as captured:
        asyncio.run(provider.run_structured("prompt", BuiltResumeResult))

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
        asyncio.run(provider.run_structured("prompt", BuiltResumeResult))

    assert captured.value.category == expected_category


def test_provider_requires_api_key_except_for_ollama() -> None:
    with pytest.raises(AIProviderError) as captured:
        LangChainProvider(name="groq", model="some-model", api_key="")
    assert captured.value.category == "missing_api_key"

    LangChainProvider(name="ollama", model="qwen3:8b", base_url="http://localhost:11434")
