import json
import re

import httpx
from pydantic import ValidationError

from app.providers.base import AIProviderError, AIProvider, create_prompt
from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, key_api: str, model: str, timeout: float = 120.0) -> None:

        if not key_api.strip():
            raise AIProviderError(
                "A variável GEMINI_API_KEY não foi configurada.",
                category="missing_api_key",
            )

        self.key_api = key_api
        self.model = model
        self.timeout = timeout

        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )

    async def generate_completion(
        self,
        request: AnalysisRequest,
        base_result: AnalysisResult,
    ) -> AIComplement:

        analysis = await self.generate_structured_analysis(request, base_result)
        return AIComplement(
            generated_summary=analysis.contextual_summary,
            suggestions=analysis.improvement_suggestions + analysis.next_steps,
        )

    async def generate_structured_analysis(self, request, base_result):
        # Implementation note.
        corpo = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": create_prompt(request, base_result)}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(
                    self.url,
                    params={"key": self.key_api},
                    json=corpo,
                )

                response.raise_for_status()

            content = extract_gemini_text(response.json())
            content = remove_json_fence(content)

            return AIAnalysisResponse.model_validate(json.loads(content))

        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            category = {
                400: "invalid_request",
                401: "auth_error_401",
                403: "permission_error_403",
                404: "invalid_model",
                413: "request_too_large",
                429: "rate_limit_429",
            }.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise AIProviderError(
                f"O Gemini recusou a requisição com status {status}.",
                category=category,
                status_http=status,
            ) from error

        except httpx.TimeoutException as error:
            raise AIProviderError(
                "O Gemini excedeu o tempo limite.", category="timeout"
            ) from error

        except httpx.HTTPError as error:
            raise AIProviderError(
                "Não foi possível conectar ao Gemini.", category="network_error"
            ) from error

        except json.JSONDecodeError as error:
            raise AIProviderError(
                "O Gemini retornou JSON inválido.", category="invalid_json"
            ) from error

        except ValidationError as error:
            raise AIProviderError(
                "O Gemini retornou dados fora do schema esperado.",
                category="schema_validation_error",
            ) from error

        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise AIProviderError(
                "O Gemini retornou uma resposta vazia ou inválida.",
                category="invalid_json",
            ) from error

    async def run_structured_task(self, task, prompt, schema, temperature=0.1):
        corpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                 "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(self.url, params={"key": self.key_api}, json=corpo)
                if response.status_code == 400:
                    # Implementation note.
                    corpo["generationConfig"].pop("responseMimeType", None)
                    response = await cliente.post(self.url, params={"key": self.key_api}, json=corpo)
                response.raise_for_status()
            try:
                content = remove_json_fence(extract_gemini_text(response.json()))
            except (KeyError, IndexError, TypeError, ValueError) as error:
                raise AIProviderError("Resposta vazia na etapa.", category="empty_response") from error
            return schema.model_validate(json.loads(content)).model_dump()
        except AIProviderError:
            raise
        except httpx.TimeoutException as error:
            raise AIProviderError("Tempo limite da etapa excedido.", category="timeout") from error
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            category = {413: "request_too_large", 429: "rate_limit_429"}.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise AIProviderError("Falha HTTP na etapa.", category=category, status_http=status) from error
        except json.JSONDecodeError as error:
            category = "json_truncated" if content.lstrip().startswith(("{", "[")) and not content.rstrip().endswith(("}", "]")) else "invalid_json"
            raise AIProviderError("JSON inválido na etapa.", category=category) from error
        except ValidationError as error:
            raise AIProviderError("Schema inválido na etapa.", category="schema_validation_error") from error
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            raise AIProviderError("Resposta inválida na etapa.", category="invalid_json") from error


def extract_gemini_text(response: dict) -> str:
    """Extract text from the first native Gemini candidate."""
    text = response["candidates"][0]["content"]["parts"][0]["text"]
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Resposta Gemini sem texto")
    return text.strip()


def remove_json_fence(text: str) -> str:
    """Accept fenced JSON without accepting additional text."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    return text.strip()
