import json

import httpx
from pydantic import ValidationError

from app.providers.base import AIProviderError, AIProvider, create_prompt
from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse


class OpenAICompatibleProvider(AIProvider):
    """Share authentication, requests, and validation across compatible APIs."""

    def __init__(
        self,
        name: str,
        key_api: str,
        key_variable: str,
        model: str,
        url: str,
        timeout: float = 30.0,
    ) -> None:

        if not key_api.strip():
            raise AIProviderError(
                f"A variável {key_variable} não foi configurada.",
                category="missing_api_key",
            )

        self.name = name
        self.key_api = key_api
        self.model = model
        self.url = url
        self.timeout = timeout

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
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Responda somente com JSON válido."},
                {"role": "user", "content": create_prompt(request, base_result)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        # cabecalho padraozao
        cabecalhos = {
            "Authorization": f"Bearer {self.key_api}",
            "Content-Type": "application/json",
        }

        try:
            # Implementation note.
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(self.url, headers=cabecalhos, json=corpo)

                response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]

            # Implementation note.
            #
            return AIAnalysisResponse.model_validate(json.loads(content))

        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            category = {
                400: "invalid_request",
                401: "auth_error_401",
                403: "permission_error_403",
                404: "invalid_model",
                429: "rate_limit_429",
            }.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise AIProviderError(
                f"O provedor {self.name} recusou a requisição com status "
                f"{status}.",
                category=category,
                status_http=status,
            ) from error

        except httpx.TimeoutException as error:
            raise AIProviderError(
                f"O provedor {self.name} excedeu o tempo limite.",
                category="timeout",
            ) from error

        except httpx.HTTPError as error:
            raise AIProviderError(
                f"Não foi possível conectar ao provedor {self.name}.",
                category="network_error",
            ) from error

        except json.JSONDecodeError as error:
            raise AIProviderError(
                f"O provedor {self.name} retornou JSON inválido.",
                category="invalid_json",
            ) from error

        except ValidationError as error:
            raise AIProviderError(
                f"O provedor {self.name} retornou dados fora do schema.",
                category="schema_validation_error",
            ) from error

        except (KeyError, TypeError) as error:
            raise AIProviderError(
                f"O provedor {self.name} retornou uma resposta vazia ou inválida.",
                category="invalid_json",
            ) from error

    async def run_structured_task(self, task, prompt, schema, temperature=0.1):
        corpo = {"model": self.model, "messages": [
            {"role": "system", "content": "Responda somente com JSON válido."},
            {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": temperature}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(self.url, headers={
                    "Authorization": f"Bearer {self.key_api}", "Content-Type": "application/json"}, json=corpo)
                if response.status_code == 400:
                    # Implementation note.
                    corpo.pop("response_format", None)
                    response = await cliente.post(self.url, headers={
                        "Authorization": f"Bearer {self.key_api}", "Content-Type": "application/json"}, json=corpo)
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if not content or not content.strip():
                raise AIProviderError("Resposta vazia.", category="empty_response")
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
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise AIProviderError("Resposta inválida na etapa.", category="invalid_json") from error
