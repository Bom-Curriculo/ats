import os
from collections.abc import Callable

from app.providers.base import ErroProvedorIA, ProvedorIA
from app.providers.fabrica import criar_provedor
from app.schemas.analise import (
    FallbackIA,
    ErroProviderSanitizado,
    InformacoesPrivacidade,
    ResultadoAnalise,
    SolicitacaoAnalise,
)
from app.services.analisador_ats import analisar_curriculo, analisar_curriculo_com_ia
from app.services.sanitizador_privacidade import sanitizar_dados_pessoais

PROVEDORES_SUPORTADOS = ("groq", "gemini", "deepseek", "openai", "ollama")
CADEIA_PADRAO = ",".join(PROVEDORES_SUPORTADOS)
VARIAVEIS_CHAVE = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def obter_cadeia_provedores() -> list[str]:
    """remover duplicatas"""

    selecionado = os.getenv("IA_PROVIDER", "auto").strip().lower() or "auto"
    if selecionado != "auto":
        if selecionado not in PROVEDORES_SUPORTADOS and selecionado != "mock":
            raise ErroProvedorIA(f"Provedor '{selecionado}' não reconhecido.")
        return [selecionado]
    bruta = os.getenv("IA_PROVIDER_CHAIN", CADEIA_PADRAO)
    cadeia = list(
        dict.fromkeys(item.strip().lower() for item in bruta.split(",") if item.strip())
    )
    invalidos = [
        item for item in cadeia if item not in PROVEDORES_SUPORTADOS and item != "mock"
    ]
    if invalidos:
        raise ErroProvedorIA("IA_PROVIDER_CHAIN contém provedor não reconhecido.")
    if not cadeia:
        raise ErroProvedorIA("IA_PROVIDER_CHAIN não possui provedores válidos.")
    return cadeia


def provedor_configurado(nome: str) -> bool:
    """sem retorno de conteúdo"""

    if nome in VARIAVEIS_CHAVE:
        return bool(os.getenv(VARIAVEIS_CHAVE[nome], "").strip())
    if nome == "ollama":
        return bool(
            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
            and os.getenv("OLLAMA_MODEL", "qwen3:8b").strip()
        )
    return nome == "mock"


def _erro_seguro(nome: str, modelo: str | None, erro: Exception) -> ErroProviderSanitizado:
    """Converte qualquer falha em msg fixa de forma direta"""

    rotulo = nome.capitalize()
    categoria = getattr(erro, "categoria", "unknown_provider_error")
    status = getattr(erro, "status_http", None)
    mensagens = {
        "missing_api_key": f"{rotulo} não possui configuração mínima.",
        "auth_error_401": f"{rotulo} recusou a autenticação.",
        "permission_error_403": f"{rotulo} recusou a permissão solicitada.",
        "rate_limit_429": f"{rotulo} atingiu o limite de requisições.",
        "timeout": f"{rotulo} excedeu o tempo limite.",
        "network_error": f"Não foi possível conectar ao {rotulo}.",
        "invalid_model": f"{rotulo} não reconheceu ou não disponibilizou o modelo configurado.",
        "invalid_request": f"{rotulo} recusou o formato da requisição.",
        "request_too_large": f"{rotulo} recusou a requisição por exceder o tamanho permitido.",
        "invalid_json": f"{rotulo} retornou JSON inválido ou vazio.",
        "json_truncated": f"{rotulo} retornou JSON aparentemente truncado.",
        "empty_response": f"{rotulo} retornou resposta vazia.",
        "schema_validation_error": f"{rotulo} retornou dados fora do schema esperado.",
        "provider_unavailable": f"{rotulo} está temporariamente indisponível.",
        "unknown_provider_error": f"{rotulo} retornou erro não classificado.",
    }
    return ErroProviderSanitizado(
        provider=nome,
        modelo=modelo,
        categoria_erro=categoria,
        status_http=status,
        mensagem_segura=mensagens.get(categoria, mensagens["unknown_provider_error"]),
    )


def _ia_habilitada(solicitacao: SolicitacaoAnalise) -> bool:
    """A opção explícita da requisição prevalece sobre o default do ambiente."""
    if solicitacao.usar_ia is not None:
        return solicitacao.usar_ia
    return os.getenv("USAR_IA_PADRAO", "true").strip().lower() not in {
        "0",
        "false",
        "nao",
        "não",
        "off",
    }


async def executar_analise_com_fallback(
    solicitacao: SolicitacaoAnalise,
    fabrica: Callable[[str], ProvedorIA] = criar_provedor,
) -> ResultadoAnalise:
    """Executa análise local e filtra"""

    resultado = analisar_curriculo(solicitacao)
    curriculo = sanitizar_dados_pessoais(solicitacao.curriculo_texto)
    vaga = sanitizar_dados_pessoais(solicitacao.vaga_texto)
    itens_removidos = list(
        dict.fromkeys(curriculo.itens_removidos + vaga.itens_removidos)
    )
    segura = solicitacao.model_copy(
        update={
            "curriculo_texto": curriculo.texto_sanitizado,
            "vaga_texto": vaga.texto_sanitizado,
            "fontes_curriculo": [],
        }
    )
    if not _ia_habilitada(solicitacao):
        return resultado.model_copy(
            update={
                "fallback_local_usado": True,
                "privacidade": InformacoesPrivacidade(
                    dados_sensiveis_detectados=bool(itens_removidos),
                    itens_removidos_antes_ia=itens_removidos,
                    texto_enviado_para_ia_foi_sanitizado=False,
                ),
            }
        )
    cadeia = obter_cadeia_provedores()
    tentados: list[str] = []
    ignorados: list[str] = []
    ultimo_erro: str | None = None
    erros: list[str] = []
    detalhes_erros: list[ErroProviderSanitizado] = []


    for indice, nome in enumerate(cadeia):
        if not provedor_configurado(nome):
            ignorados.append(nome)
            continue


        tentados.append(nome)
        provedor: ProvedorIA | None = None
        try:
            provedor = fabrica(nome)
            enriquecido = await analisar_curriculo_com_ia(
                segura, provedor, propagar_erro_provider=True
            )


            if enriquecido.fallback_local_usado or enriquecido.analise_ia is None:
                ultimo_erro = (
                    f"{nome.capitalize()} retornou resposta vazia, inválida ou reprovada pela validação."
                )
                erros.append(ultimo_erro)
                detalhes_erros.append(
                    ErroProviderSanitizado(
                        provider=nome,
                        modelo=provedor.modelo,
                        categoria_erro="schema_validation_error",
                        mensagem_segura=ultimo_erro,
                    )
                )
                continue


            fallback = FallbackIA(
                fallback_usado=indice > 0 or len(tentados) > 1,
                provedores_tentados=tentados,
                provedores_ignorados_por_configuracao=ignorados,
                ultimo_erro_sanitizado=ultimo_erro,
                erros_provedores_sanitizados=erros,
            )


            return enriquecido.model_copy(
                update={
                    "fallback_ia": fallback,
                    "provedores_tentados": tentados,
                    "erros_provedores_sanitizados": erros,
                    "detalhes_erros_provedores": detalhes_erros,
                    "privacidade": InformacoesPrivacidade(
                        dados_sensiveis_detectados=bool(itens_removidos),
                        itens_removidos_antes_ia=itens_removidos,
                        texto_enviado_para_ia_foi_sanitizado=True,
                    ),
                }
            )


        except Exception as erro:
            # Não tem log do erro bruto, prompt, currículo ou configuração.
            detalhe = _erro_seguro(nome, getattr(provedor, "modelo", None), erro)
            ultimo_erro = detalhe.mensagem_segura
            erros.append(ultimo_erro)
            detalhes_erros.append(detalhe)

    fallback = FallbackIA(
        fallback_usado=True,
        provedores_tentados=tentados,
        provedores_ignorados_por_configuracao=ignorados,
        ultimo_erro_sanitizado=ultimo_erro,
        erros_provedores_sanitizados=erros,
    )


    return resultado.model_copy(
        update={
            "fallback_local_usado": True,
            "provedor_ia": "sem_ia",
            "modelo_ia": None,
            "fallback_ia": fallback,
            "provedores_tentados": tentados,
            "erros_provedores_sanitizados": erros,
            "detalhes_erros_provedores": detalhes_erros,
            "privacidade": InformacoesPrivacidade(
                dados_sensiveis_detectados=bool(itens_removidos),
                itens_removidos_antes_ia=itens_removidos,
                texto_enviado_para_ia_foi_sanitizado=bool(tentados),
            ),
        }
    )
