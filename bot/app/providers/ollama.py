import json

import httpx
from pydantic import ValidationError

from app.providers.base import AIProviderError, AIProvider, create_prompt
from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, model: str, base_url: str, timeout: float = 120.0) -> None:

        self.model = model

        # Implementation note.
        self.url = f"{base_url.rstrip('/')}/api/chat"

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
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(self.url, json=corpo)

                response.raise_for_status()

            content = response.json()["message"]["content"]

            return AIAnalysisResponse.model_validate(json.loads(content))

        except httpx.HTTPStatusError as error:
            raise AIProviderError(
                f"Ollama recusou a requisição com status {error.response.status_code}."
            ) from error

        except httpx.HTTPError as error:
            raise AIProviderError(
                "Não foi possível conectar ao Ollama. Verifique se o serviço está ativo."
            ) from error

        except (KeyError, TypeError, json.JSONDecodeError, ValidationError) as error:
            raise AIProviderError(
                "O Ollama retornou uma resposta em formato inválido."
            ) from error

    async def run_structured_task(self, task, prompt, schema, temperature=0.1):
        corpo = {"model": self.model, "messages": [
            {"role": "system", "content": "Responda somente com JSON válido."},
            {"role": "user", "content": prompt}], "format": "json", "stream": False,
            "options": {"temperature": temperature}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                response = await cliente.post(self.url, json=corpo)
                if response.status_code == 400:
                    # Implementation note.
                    corpo.pop("format", None)
                    response = await cliente.post(self.url, json=corpo)
                response.raise_for_status()
            content = response.json()["message"]["content"]
            if not content or not content.strip():
                raise AIProviderError("Resposta vazia.", category="empty_response")
            return schema.model_validate(json.loads(content)).model_dump()
        except AIProviderError:
            raise
        except httpx.TimeoutException as error:
            raise AIProviderError("Tempo limite da etapa excedido.", category="timeout") from error
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            raise AIProviderError("Falha HTTP na etapa.", category="rate_limit_429" if status == 429 else "provider_unavailable", status_http=status) from error
        except json.JSONDecodeError as error:
            category = "json_truncated" if content.lstrip().startswith(("{", "[")) and not content.rstrip().endswith(("}", "]")) else "invalid_json"
            raise AIProviderError("JSON inválido na etapa.", category=category) from error
        except ValidationError as error:
            raise AIProviderError("Schema inválido na etapa.", category="schema_validation_error") from error
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise AIProviderError("Resposta inválida na etapa.", category="invalid_json") from error
