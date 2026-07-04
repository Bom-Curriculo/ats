import asyncio

import pytest
from app.providers.base import AIProviderError
from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ai.ai_manager import AIManager


class ProviderFake(MockProvider):
    def __init__(self, name: str, should_fail: bool = False, captures: list | None = None):

        super().__init__(model=f"modelo-{name}", summary=f"Resposta de {name}.")

        self.name = name

        self.should_fail = should_fail

        self.captures = captures

    async def generate_completion(self, request, base_result):

        if self.captures is not None:
            self.captures.append((self.name, request))

        if self.should_fail:
            raise AIProviderError(f"Falha simulada de {self.name}")

        return await super().generate_completion(request, base_result)


def request() -> AnalysisRequest:

    return AnalysisRequest(
        resume_text="COMPETÊNCIAS\nPython", job_text="Requisitos:\nPython"
    )


def configure_keys(monkeypatch):

    for name in ("GROQ", "GEMINI", "DEEPSEEK", "OPENAI"):
        monkeypatch.setenv(f"{name}_API_KEY", "chave-ficticia-para-teste")


def test_ai_manager_behavior_01(monkeypatch) -> None:

    configure_keys(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    calls = []

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == ["groq"]

    assert result.ai_provider == "groq"

    assert result.ai_fallback.fallback_used is False


def test_ai_manager_behavior_02(monkeypatch) -> None:

    configure_keys(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: ProviderFake(name, should_fail=name == "groq")
        )
    )

    assert result.ai_provider == "gemini"

    assert result.ai_fallback.attempted_providers == ["groq", "gemini"]

    assert result.ai_fallback.fallback_used is True

    assert "Groq" in result.ai_fallback.last_sanitized_error


def test_ai_manager_behavior_03(monkeypatch) -> None:

    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(request(), lambda name: ProviderFake(name))
    )

    assert result.ai_provider == "gemini"
    assert result.ai_fallback.providers_skipped_by_configuration == ["groq"]
    assert result.ai_fallback.attempted_providers == ["gemini"]


def test_ai_manager_behavior_04(monkeypatch) -> None:

    configure_keys(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: ProviderFake(name, should_fail=True)
        )
    )

    assert result.local_fallback_used is True
    assert result.ai_provider == "sem_ia"
    assert result.ai_fallback.attempted_providers == ["groq", "gemini"]
    assert len(result.sanitized_provider_errors) == 2


@pytest.mark.parametrize(
    "selected,forbidden", [("groq", "deepseek"), ("deepseek", "groq")]
)
def test_ai_manager_behavior_05(
    monkeypatch, selected, forbidden
) -> None:

    configure_keys(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", selected)

    calls = []

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == [selected]

    assert result.ai_provider == selected

    assert forbidden not in calls


def test_ai_manager_behavior_06(monkeypatch) -> None:

    configure_keys(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    captures = []

    input_request = AnalysisRequest(
        resume_text="ana@example.com (81) 99999-1234 COMPETÊNCIAS: Python",
        job_text="Requisitos: Python",
    )

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            input_request,
            lambda name: ProviderFake(name, should_fail=name == "groq", captures=captures),
        )
    )

    assert len(captures) == 2

    for _, received in captures:
        assert "ana@example.com" not in received.resume_text

        assert "99999-1234" not in received.resume_text

    assert result.privacy.items_removed_before_ai == ["email", "phone"]


def test_invalid_json_tries_next_provider(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    calls = []

    def factory(name):
        calls.append(name)
        if name == "groq":
            provider = MockProvider(structured_response="resposta sem JSON")
            provider.name = name
            return provider
        return ProviderFake(name)

    result = asyncio.run(AIManager().run_analysis_with_fallback(request(), factory))

    assert calls == ["groq", "gemini"]
    assert result.ai_provider == "gemini"
    assert result.ai_fallback.fallback_used is True
    assert "invalid" in result.sanitized_provider_errors[0]


def test_valid_low_score_does_not_change_provider(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    calls = []
    input_request = AnalysisRequest(
        resume_text="COMPETÊNCIAS\nPython",
        job_text="Requisitos obrigatórios:\nKubernetes",
    )

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            input_request, lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert result.ats_score == 0
    assert calls == ["groq"]
    assert result.ai_provider == "groq"


def test_ai_manager_behavior_09(monkeypatch) -> None:
    configure_keys(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "groq")
    calls = []

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(),
            lambda name: calls.append(name) or ProviderFake(name, should_fail=True),
        )
    )

    assert calls == ["groq"]
    assert result.local_fallback_used is True
    assert result.ai_provider == "sem_ia"


def test_use_ai_defaults_to_false_without_calling_provider(monkeypatch) -> None:
    monkeypatch.setenv("USAR_IA_PADRAO", "false")
    calls = []

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: calls.append(name) or ProviderFake(name)
        )
    )

    assert calls == []
    assert result.local_fallback_used is True
    assert result.privacy.ai_text_was_sanitized is False


def test_ai_manager_behavior_11(
    monkeypatch, caplog
) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    secret = "Bearer token-super-secreto-123456789"

    class ProviderInseguro(ProviderFake):
        async def generate_completion(self, request, base_result):
            raise AIProviderError(
                f"Authorization: {secret}; prompt complete confidencial"
            )

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: ProviderInseguro(name)
        )
    )
    serialized = result.model_dump_json()

    assert secret not in caplog.text
    assert secret not in serialized
    assert "Authorization" not in serialized
    assert "prompt complete confidencial" not in serialized


@pytest.mark.parametrize(
    "category,status",
    [
        ("auth_error_401", 401),
        ("permission_error_403", 403),
        ("rate_limit_429", 429),
        ("timeout", None),
    ],
)
def test_error_groq_returns_diagnostic_structured_sanitized(
    monkeypatch, category, status
) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    class GroqComFalha(ProviderFake):
        async def generate_completion(self, request, base_result):
            raise AIProviderError(
                "detail interno que não deve sair",
                category=category,
                status_http=status,
            )

    result = asyncio.run(
        AIManager().run_analysis_with_fallback(
            request(), lambda name: GroqComFalha(name)
        )
    )
    detail = result.provider_error_details[0]

    assert detail.provider == "groq"
    assert detail.error_category == category
    assert detail.status_http == status
    assert "detail interno" not in result.model_dump_json()
