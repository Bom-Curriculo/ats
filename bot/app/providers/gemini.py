import json
import re

import httpx
from pydantic import ValidationError

from app.providers.base import ErroProvedorIA, ProvedorIA, criar_prompt
from app.schemas.analise import ComplementoIA, ResultadoAnalise, SolicitacaoAnalise
from app.schemas.analise_ia import RespostaAnaliseIA


class GeminiProvider(ProvedorIA):
    nome = "gemini"

    def __init__(self, chave_api: str, modelo: str, timeout: float = 120.0) -> None:

        if not chave_api.strip():
            raise ErroProvedorIA(
                "A variável GEMINI_API_KEY não foi configurada.",
                categoria="missing_api_key",
            )

        self.chave_api = chave_api
        self.modelo = modelo
        self.timeout = timeout

        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent"
        )

    async def gerar_complemento(
        self,
        solicitacao: SolicitacaoAnalise,
        resultado_base: ResultadoAnalise,
    ) -> ComplementoIA:

        analise = await self.gerar_analise_estruturada(solicitacao, resultado_base)
        return ComplementoIA(
            resumo_gerado=analise.resumo_contextual,
            sugestoes=analise.sugestoes_de_melhoria + analise.proximos_passos,
        )

    async def gerar_analise_estruturada(self, solicitacao, resultado_base):
        # body no padrao que o gemini espera
        corpo = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": criar_prompt(solicitacao, resultado_base)}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(
                    self.url,
                    params={"key": self.chave_api},
                    json=corpo,
                )

                resposta.raise_for_status()

            conteudo = extrair_texto_gemini(resposta.json())
            conteudo = remover_cerca_json(conteudo)

            return RespostaAnaliseIA.model_validate(json.loads(conteudo))

        except httpx.HTTPStatusError as erro:
            status = erro.response.status_code
            categoria = {
                400: "invalid_request",
                401: "auth_error_401",
                403: "permission_error_403",
                404: "invalid_model",
                413: "request_too_large",
                429: "rate_limit_429",
            }.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise ErroProvedorIA(
                f"O Gemini recusou a requisição com status {status}.",
                categoria=categoria,
                status_http=status,
            ) from erro

        except httpx.TimeoutException as erro:
            raise ErroProvedorIA(
                "O Gemini excedeu o tempo limite.", categoria="timeout"
            ) from erro

        except httpx.HTTPError as erro:
            raise ErroProvedorIA(
                "Não foi possível conectar ao Gemini.", categoria="network_error"
            ) from erro

        except json.JSONDecodeError as erro:
            raise ErroProvedorIA(
                "O Gemini retornou JSON inválido.", categoria="invalid_json"
            ) from erro

        except ValidationError as erro:
            raise ErroProvedorIA(
                "O Gemini retornou dados fora do schema esperado.",
                categoria="schema_validation_error",
            ) from erro

        except (KeyError, IndexError, TypeError, ValueError) as erro:
            raise ErroProvedorIA(
                "O Gemini retornou uma resposta vazia ou inválida.",
                categoria="invalid_json",
            ) from erro

    async def executar_tarefa_estruturada(self, tarefa, prompt, schema, temperatura=0.1):
        corpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                 "generationConfig": {"temperature": temperatura, "responseMimeType": "application/json"}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(self.url, params={"key": self.chave_api}, json=corpo)
                if resposta.status_code == 400:
                    # Alguns modelos/versões Gemini recusam responseMimeType.
                    corpo["generationConfig"].pop("responseMimeType", None)
                    resposta = await cliente.post(self.url, params={"key": self.chave_api}, json=corpo)
                resposta.raise_for_status()
            try:
                conteudo = remover_cerca_json(extrair_texto_gemini(resposta.json()))
            except (KeyError, IndexError, TypeError, ValueError) as erro:
                raise ErroProvedorIA("Resposta vazia na etapa.", categoria="empty_response") from erro
            return schema.model_validate(json.loads(conteudo)).model_dump()
        except ErroProvedorIA:
            raise
        except httpx.TimeoutException as erro:
            raise ErroProvedorIA("Tempo limite da etapa excedido.", categoria="timeout") from erro
        except httpx.HTTPStatusError as erro:
            status = erro.response.status_code
            categoria = {413: "request_too_large", 429: "rate_limit_429"}.get(status, "provider_unavailable" if status >= 500 else "invalid_request")
            raise ErroProvedorIA("Falha HTTP na etapa.", categoria=categoria, status_http=status) from erro
        except json.JSONDecodeError as erro:
            categoria = "json_truncated" if conteudo.lstrip().startswith(("{", "[")) and not conteudo.rstrip().endswith(("}", "]")) else "invalid_json"
            raise ErroProvedorIA("JSON inválido na etapa.", categoria=categoria) from erro
        except ValidationError as erro:
            raise ErroProvedorIA("Schema inválido na etapa.", categoria="schema_validation_error") from erro
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as erro:
            raise ErroProvedorIA("Resposta inválida na etapa.", categoria="invalid_json") from erro


def extrair_texto_gemini(resposta: dict) -> str:
    """Extrai somente o texto do primeiro candidato no formato nativo Gemini."""
    texto = resposta["candidates"][0]["content"]["parts"][0]["text"]
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Resposta Gemini sem texto")
    return texto.strip()


def remover_cerca_json(texto: str) -> str:
    """Tolera JSON cercado por Markdown sem aceitar texto adicional."""
    texto = texto.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.I)
    return texto.strip()
