import asyncio

from app.providers.base import create_prompt
from app.providers.mock import MockProvider
from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume_with_ai
from app.services.normalization.text_normalizer import normalize_resume_text
from app.services.privacy.sanitizer import PrivacySanitizer

"""Privacy and PDF-extracted text-cleaning cases."""


def test_privacy_normalization_behavior_01() -> None:

    email = "ana.teste@example.com"

    telefone = "(81) 99999-1234"

    result = PrivacySanitizer().sanitize(f"Contato: {email} ou {telefone}")

    # trocou corretamente pelos marcadores
    assert (
        result.text_sanitized == "Contato: [EMAIL_REMOVED] ou [PHONE_REMOVED]"
    )

    assert result.items_removed == ["email", "phone"]

    # Implementation note.
    assert email not in repr(result)

    assert telefone not in repr(result)


def test_normalizer_corrects_spaced_title() -> None:

    assert normalize_resume_text("C O M P E T Ê N C I A S") == "COMPETÊNCIAS"


class CaptureProvider(MockProvider):
    received_request: AnalysisRequest | None = None

    async def generate_completion(self, request, base_result):

        # Implementation note.
        self.received_request = request

        return await super().generate_completion(request, base_result)


def test_privacy_normalization_behavior_03() -> None:

    provider = CaptureProvider()

    request = AnalysisRequest(
        resume_text="Ana, ana@example.com, (81) 99999-1234. Experiência: React.",
        job_text="Requisitos obrigatórios:\nReact",
        use_ai=True,
    )

    result = asyncio.run(analyze_resume_with_ai(request, provider))

    assert provider.received_request is not None

    # Technical note removed during English standardization.
    assert "ana@example.com" not in provider.received_request.resume_text

    assert "99999-1234" not in provider.received_request.resume_text

    assert result.privacy is not None

    assert result.privacy.ai_text_was_sanitized is True

    assert result.privacy.items_removed_before_ai == ["email", "phone"]


def test_privacy_normalization_behavior_04() -> None:

    request = AnalysisRequest(
        resume_text="Contato ana@example.com e experiência com React.",
        job_text="React",
    )

    from app.services.ats_analyzer import analyze_resume

    prompt = create_prompt(request, analyze_resume(request))

    # Technical note removed during English standardization.
    assert "ana@example.com" not in prompt

    assert "[EMAIL_REMOVED]" in prompt

    assert "Do not invent experience" in prompt


def test_privacy_normalization_behavior_05() -> None:
    pessoais = (
        "teste@example.com",
        "(81) 99999-1234",
        "https://linkedin.com/in/teste",
        "https://github.com/teste",
        "https://portfolio-teste.example.com",
    )
    request = AnalysisRequest(
        resume_text="Contato: " + " ".join(pessoais) + " HABILIDADES: Python",
        job_text="Requisitos: Python",
    )
    from app.services.ats_analyzer import analyze_resume

    prompt = create_prompt(request, analyze_resume(request))

    assert not any(value in prompt for value in pessoais)
