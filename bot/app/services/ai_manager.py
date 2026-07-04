import os
from collections.abc import Callable

from app.providers.base import AIProviderError, AIProvider
from app.providers.factory import create_provider
from app.schemas.analysis import (
    AIFallback,
    SanitizedProviderError,
    PrivacyInformation,
    AnalysisResult,
    AnalysisRequest,
)
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai
from app.services.privacy_sanitizer import sanitize_personal_data

SUPPORTED_PROVIDERS = ("groq", "gemini", "deepseek", "openai", "ollama")
DEFAULT_CHAIN = ",".join(SUPPORTED_PROVIDERS)
KEY_VARIABLES = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def get_provider_chain() -> list[str]:
    """remover duplicatas"""

    selected = os.getenv("IA_PROVIDER", "auto").strip().lower() or "auto"
    if selected != "auto":
        if selected not in SUPPORTED_PROVIDERS and selected != "mock":
            raise AIProviderError(f"Provedor '{selected}' não reconhecido.")
        return [selected]
    raw = os.getenv("IA_PROVIDER_CHAIN", DEFAULT_CHAIN)
    cadeia = list(
        dict.fromkeys(item.strip().lower() for item in raw.split(",") if item.strip())
    )
    invalidos = [
        item for item in cadeia if item not in SUPPORTED_PROVIDERS and item != "mock"
    ]
    if invalidos:
        raise AIProviderError("IA_PROVIDER_CHAIN contém provedor não reconhecido.")
    if not cadeia:
        raise AIProviderError("IA_PROVIDER_CHAIN não possui provedores válidos.")
    return cadeia


def is_provider_configured(name: str) -> bool:
    """Return no sensitive provider content."""

    if name in KEY_VARIABLES:
        return bool(os.getenv(KEY_VARIABLES[name], "").strip())
    if name == "ollama":
        return bool(
            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
            and os.getenv("OLLAMA_MODEL", "qwen3:8b").strip()
        )
    return name == "mock"


def _safe_error(name: str, model: str | None, error: Exception) -> SanitizedProviderError:
    """Convert provider failures into fixed safe messages."""

    label = name.capitalize()
    category = getattr(error, "category", "unknown_provider_error")
    status = getattr(error, "status_http", None)
    mensagens = {
        "missing_api_key": f"{label} não possui configuração mínima.",
        "auth_error_401": f"{label} recusou a autenticação.",
        "permission_error_403": f"{label} recusou a permissão solicitada.",
        "rate_limit_429": f"{label} atingiu o limite de requisições.",
        "timeout": f"{label} excedeu o tempo limite.",
        "network_error": f"Não foi possível conectar ao {label}.",
        "invalid_model": f"{label} não reconheceu ou não disponibilizou o modelo configurado.",
        "invalid_request": f"{label} recusou o formato da requisição.",
        "request_too_large": f"{label} recusou a requisição por exceder o tamanho permitido.",
        "invalid_json": f"{label} retornou JSON inválido ou vazio.",
        "json_truncated": f"{label} retornou JSON aparentemente truncado.",
        "empty_response": f"{label} retornou resposta vazia.",
        "schema_validation_error": f"{label} retornou dados fora do schema esperado.",
        "provider_unavailable": f"{label} está temporariamente indisponível.",
        "unknown_provider_error": f"{label} retornou erro não classificado.",
    }
    return SanitizedProviderError(
        provider=name,
        model=model,
        error_category=category,
        status_http=status,
        safe_message=mensagens.get(category, mensagens["unknown_provider_error"]),
    )


def _is_ai_enabled(request: AnalysisRequest) -> bool:
    """An explicit request option overrides the environment default."""
    if request.use_ai is not None:
        return request.use_ai
    return os.getenv("USAR_IA_PADRAO", "true").strip().lower() not in {
        "0",
        "false",
        "nao",
        "não",
        "off",
    }


async def run_analysis_with_fallback(
    request: AnalysisRequest,
    factory: Callable[[str], AIProvider] = create_provider,
) -> AnalysisResult:
    """Run local analysis and safely apply optional AI enrichment."""

    result = analyze_resume(request)
    resume = sanitize_personal_data(request.resume_text)
    job = sanitize_personal_data(request.job_text)
    items_removidos = list(
        dict.fromkeys(resume.items_removidos + job.items_removidos)
    )
    safe = request.model_copy(
        update={
            "resume_text": resume.text_sanitized,
            "job_text": job.text_sanitized,
            "resume_sources": [],
        }
    )
    if not _is_ai_enabled(request):
        return result.model_copy(
            update={
                "local_fallback_used": True,
                "privacy": PrivacyInformation(
                    sensitive_data_detected=bool(items_removidos),
                    items_removed_before_ai=items_removidos,
                    ai_text_was_sanitized=False,
                ),
            }
        )
    cadeia = get_provider_chain()
    tentados: list[str] = []
    ignorados: list[str] = []
    ultimo_error: str | None = None
    errors: list[str] = []
    details_errors: list[SanitizedProviderError] = []


    for indice, name in enumerate(cadeia):
        if not is_provider_configured(name):
            ignorados.append(name)
            continue


        tentados.append(name)
        provider: AIProvider | None = None
        try:
            provider = factory(name)
            enriquecido = await analyze_resume_with_ai(
                safe, provider, propagar_error_provider=True
            )


            if enriquecido.local_fallback_used or enriquecido.ai_analysis is None:
                ultimo_error = (
                    f"{name.capitalize()} retornou resposta vazia, inválida ou reprovada pela validação."
                )
                errors.append(ultimo_error)
                details_errors.append(
                    SanitizedProviderError(
                        provider=name,
                        model=provider.model,
                        error_category="schema_validation_error",
                        safe_message=ultimo_error,
                    )
                )
                continue


            fallback = AIFallback(
                fallback_used=indice > 0 or len(tentados) > 1,
                attempted_providers=tentados,
                providers_skipped_by_configuration=ignorados,
                last_sanitized_error=ultimo_error,
                sanitized_provider_errors=errors,
            )


            return enriquecido.model_copy(
                update={
                    "ai_fallback": fallback,
                    "attempted_providers": tentados,
                    "sanitized_provider_errors": errors,
                    "provider_error_details": details_errors,
                    "privacy": PrivacyInformation(
                        sensitive_data_detected=bool(items_removidos),
                        items_removed_before_ai=items_removidos,
                        ai_text_was_sanitized=True,
                    ),
                }
            )


        except Exception as error:
            # Technical note removed during English standardization.
            detail = _safe_error(name, getattr(provider, "model", None), error)
            ultimo_error = detail.safe_message
            errors.append(ultimo_error)
            details_errors.append(detail)

    fallback = AIFallback(
        fallback_used=True,
        attempted_providers=tentados,
        providers_skipped_by_configuration=ignorados,
        last_sanitized_error=ultimo_error,
        sanitized_provider_errors=errors,
    )


    return result.model_copy(
        update={
            "local_fallback_used": True,
            "ai_provider": "sem_ia",
            "ai_model": None,
            "ai_fallback": fallback,
            "attempted_providers": tentados,
            "sanitized_provider_errors": errors,
            "provider_error_details": details_errors,
            "privacy": PrivacyInformation(
                sensitive_data_detected=bool(items_removidos),
                items_removed_before_ai=items_removidos,
                ai_text_was_sanitized=bool(tentados),
            ),
        }
    )
