import json

import httpx
from pydantic import ValidationError

from app.providers.base import ErroProvedorIA, ProvedorIA, criar_prompt
from app.schemas.analise import ComplementoIA, ResultadoAnalise, SolicitacaoAnalise
from app.schemas.analise_ia import RespostaAnaliseIA


class OllamaProvider(ProvedorIA):
    nome = "ollama"

    def __init__(self, modelo: str, base_url: str, timeout: float = 120.0) -> None:

        self.modelo = modelo

        # tira barra extra se tiver no final
        self.url = f"{base_url.rstrip('/')}/api/chat"

        self.timeout = timeout

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
        # body padrao chat do ollama
        corpo = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": "Responda somente com JSON válido."},
                {"role": "user", "content": criar_prompt(solicitacao, resultado_base)},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(self.url, json=corpo)

                resposta.raise_for_status()

            conteudo = resposta.json()["message"]["content"]

            return RespostaAnaliseIA.model_validate(json.loads(conteudo))

        except httpx.HTTPStatusError as erro:
            raise ErroProvedorIA(
                f"Ollama recusou a requisição com status {erro.response.status_code}."
            ) from erro

        except httpx.HTTPError as erro:
            raise ErroProvedorIA(
                "Não foi possível conectar ao Ollama. Verifique se o serviço está ativo."
            ) from erro

        except (KeyError, TypeError, json.JSONDecodeError, ValidationError) as erro:
            raise ErroProvedorIA(
                "O Ollama retornou uma resposta em formato inválido."
            ) from erro

    async def executar_tarefa_estruturada(self, tarefa, prompt, schema, temperatura=0.1):
        corpo = {"model": self.modelo, "messages": [
            {"role": "system", "content": "Responda somente com JSON válido."},
            {"role": "user", "content": prompt}], "format": "json", "stream": False,
            "options": {"temperature": temperatura}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                resposta = await cliente.post(self.url, json=corpo)
                if resposta.status_code == 400:
                    # descobri que alguns modelos antigos não aceitam format=json
                    corpo.pop("format", None)
                    resposta = await cliente.post(self.url, json=corpo)
                resposta.raise_for_status()
            conteudo = resposta.json()["message"]["content"]
            if not conteudo or not conteudo.strip():
                raise ErroProvedorIA("Resposta vazia.", categoria="empty_response")
            return schema.model_validate(json.loads(conteudo)).model_dump()
        except ErroProvedorIA:
            raise
        except httpx.TimeoutException as erro:
            raise ErroProvedorIA("Tempo limite da etapa excedido.", categoria="timeout") from erro
        except httpx.HTTPStatusError as erro:
            status = erro.response.status_code
            raise ErroProvedorIA("Falha HTTP na etapa.", categoria="rate_limit_429" if status == 429 else "provider_unavailable", status_http=status) from erro
        except json.JSONDecodeError as erro:
            categoria = "json_truncated" if conteudo.lstrip().startswith(("{", "[")) and not conteudo.rstrip().endswith(("}", "]")) else "invalid_json"
            raise ErroProvedorIA("JSON inválido na etapa.", categoria=categoria) from erro
        except ValidationError as erro:
            raise ErroProvedorIA("Schema inválido na etapa.", categoria="schema_validation_error") from erro
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as erro:
            raise ErroProvedorIA("Resposta inválida na etapa.", categoria="invalid_json") from erro
