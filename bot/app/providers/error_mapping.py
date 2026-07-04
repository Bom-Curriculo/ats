"""Translate LangChain/native SDK exceptions into the service's stable error categories.

Every LangChain chat-model integration (langchain-openai, langchain-groq,
langchain-google-genai, langchain-deepseek, langchain-ollama) wraps a
provider SDK that follows the openai-python exception naming convention
(``RateLimitError``, ``AuthenticationError``, ``APITimeoutError``, ...), so
matching on the exception class name is a reliable, dependency-free way to
recover a single stable category across all of them.
"""

import json

from pydantic import ValidationError

from app.providers.base import AIProviderError


def map_provider_error(provider_name: str, error: Exception) -> AIProviderError:
    if isinstance(error, AIProviderError):
        return error

    label = provider_name.capitalize()
    status_code = getattr(error, "status_code", None) or getattr(
        getattr(error, "response", None), "status_code", None
    )
    error_type = type(error).__name__

    if isinstance(error, json.JSONDecodeError):
        return AIProviderError(f"{label} returned invalid JSON.", category="invalid_json")
    if isinstance(error, ValidationError):
        return AIProviderError(
            f"{label} returned data outside the expected schema.",
            category="schema_validation_error",
        )
    if "Timeout" in error_type:
        return AIProviderError(f"{label} timed out.", category="timeout")
    if "RateLimit" in error_type or status_code == 429:
        return AIProviderError(
            f"{label} rate-limited the request.", category="rate_limit_429", status_http=429
        )
    if "Authentication" in error_type or status_code == 401:
        return AIProviderError(
            f"{label} rejected the authentication.", category="auth_error_401", status_http=401
        )
    if "PermissionDenied" in error_type or status_code == 403:
        return AIProviderError(
            f"{label} rejected the requested permission.",
            category="permission_error_403",
            status_http=403,
        )
    if "NotFound" in error_type or status_code == 404:
        return AIProviderError(
            f"{label} did not recognize or did not make available the configured model.",
            category="invalid_model",
            status_http=404,
        )
    if status_code == 413:
        return AIProviderError(
            f"{label} rejected the request for exceeding the allowed size.",
            category="request_too_large",
            status_http=413,
        )
    if "BadRequest" in error_type or "InvalidRequest" in error_type or status_code == 400:
        return AIProviderError(
            f"{label} rejected the request format.", category="invalid_request", status_http=400
        )
    if "Connection" in error_type:
        return AIProviderError(f"Could not connect to {label}.", category="network_error")
    if status_code is not None and status_code >= 500:
        return AIProviderError(
            f"{label} is temporarily unavailable.",
            category="provider_unavailable",
            status_http=status_code,
        )
    return AIProviderError(f"{label} returned an unclassified error.", category="unknown_provider_error")
