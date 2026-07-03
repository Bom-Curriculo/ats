import json

import httpx
from pydantic import ValidationError

from app.providers.base import AIProviderError, AIProvider, create_prompt
from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse


class OpenAICompatibleProvider(AIProvider):
    """Compartilha aut, requisição e validação entre APIs compatíveis."""

    def __init__(
        self,
        nome: str,
        chave_api: str,
        variavel_chave: str,
        modelo: str,
        url: str,
        timeout: float = 30.0,
    ) -> None:

        if not chave_api.strip():
            raise AIProviderError(
                f"A variável {variavel_chave} não foi configurada.",
                categoria="missing_api_key",
            )

        self.nome = nome
        self.chave_api = chave_api
        self.modelo = modelo
        self.url = url
        self.timeout = timeout

    async def gerar_complemento(
        self,
        solicitacao: AnalysisRequest,
        resultado_base: AnalysisResult,
    ) -> AIComplement:

        analise = await self.gerar_analise_estruturada(solicitacao, resultado_base)
        return AIComplement(
            resumo_gerado=analise.resumo_contextual,
            sugestoes=analise.sugestoes_de_melhoria + analise.proximos_passos,
        )

    async def gerar_analise_estruturada(self, solicitacao, resultado_base):
        # monta o corpo da req
        corpo = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": "Responda somente com JSON válido."},
                {"role": "user", "content": create_prompt(solicitacao, resultado_base)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        # cabecalho padraozao
        cabecalhos = {
            "Authorization": f"Bearer {self.chave_api}",
            "Content-Type": "application/json",
        }

        try:
            # tenta conectar e msg
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(self.url, headers=cabecalhos, json=corpo)

                resposta.raise_for_status()

            conteudo = resposta.json()["choices"][0]["message"]["content"]

            # valida e retorna
            #
            return AIAnalysisResponse.model_validate(json.loads(conteudo))

        except httpx.HTTPStatusError as erro:
            status = erro.response.status_code
            categoria = {
                400: "invalid_request",
                401: "auth_error_401",
                403: "permission_error_403",
                404: "invalid_model",
                429: "rate_limit_429",
            }.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise AIProviderError(
                f"O provedor {self.nome} recusou a requisição com status "
                f"{status}.",
                categoria=categoria,
                status_http=status,
            ) from erro

        except httpx.TimeoutException as erro:
            raise AIProviderError(
                f"O provedor {self.nome} excedeu o tempo limite.",
                categoria="timeout",
            ) from erro

        except httpx.HTTPError as erro:
            raise AIProviderError(
                f"Não foi possível conectar ao provedor {self.nome}.",
                categoria="network_error",
            ) from erro

        except json.JSONDecodeError as erro:
            raise AIProviderError(
                f"O provedor {self.nome} retornou JSON inválido.",
                categoria="invalid_json",
            ) from erro

        except ValidationError as erro:
            raise AIProviderError(
                f"O provedor {self.nome} retornou dados fora do schema.",
                categoria="schema_validation_error",
            ) from erro

        except (KeyError, TypeError) as erro:
            raise AIProviderError(
                f"O provedor {self.nome} retornou uma resposta vazia ou inválida.",
                categoria="invalid_json",
            ) from erro

    async def executar_tarefa_estruturada(self, tarefa, prompt, schema, temperatura=0.1):
        corpo = {"model": self.modelo, "messages": [
            {"role": "system", "content": "Responda somente com JSON válido."},
            {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}, "temperature": temperatura}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(self.url, headers={
                    "Authorization": f"Bearer {self.chave_api}", "Content-Type": "application/json"}, json=corpo)
                if resposta.status_code == 400:
                    # Endpoints OpenAI-compatible podem não implementar JSON mode.
                    corpo.pop("response_format", None)
                    resposta = await cliente.post(self.url, headers={
                        "Authorization": f"Bearer {self.chave_api}", "Content-Type": "application/json"}, json=corpo)
                resposta.raise_for_status()
            conteudo = resposta.json()["choices"][0]["message"]["content"]
            if not conteudo or not conteudo.strip():
                raise AIProviderError("Resposta vazia.", categoria="empty_response")
            return schema.model_validate(json.loads(conteudo)).model_dump()
        except AIProviderError:
            raise
        except httpx.TimeoutException as erro:
            raise AIProviderError("Tempo limite da etapa excedido.", categoria="timeout") from erro
        except httpx.HTTPStatusError as erro:
            status = erro.response.status_code
            categoria = {413: "request_too_large", 429: "rate_limit_429"}.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise AIProviderError("Falha HTTP na etapa.", categoria=categoria, status_http=status) from erro
        except json.JSONDecodeError as erro:
            categoria = "json_truncated" if conteudo.lstrip().startswith(("{", "[")) and not conteudo.rstrip().endswith(("}", "]")) else "invalid_json"
            raise AIProviderError("JSON inválido na etapa.", categoria=categoria) from erro
        except ValidationError as erro:
            raise AIProviderError("Schema inválido na etapa.", categoria="schema_validation_error") from erro
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as erro:
            raise AIProviderError("Resposta inválida na etapa.", categoria="invalid_json") from erro
