import os

from pydantic import BaseModel, Field

from app.providers.base import ProvedorIA
from app.schemas.analise import ResultadoAnalise, SolicitacaoAnalise
from app.schemas.analise_ia import AnaliseIARequisito, RespostaAnaliseIA
from app.schemas.pipeline_ia import (
    AvaliacaoContextualRequisito, ClassificacaoVagaIA, ResultadoPipelineIA,
)
from app.services.contexto_ia import montar_contexto_ia
from app.services.normalizador_texto import normalizar_para_comparacao
from app.services.prompts_pipeline_ia import (
    prompt_avaliacao_contextual, prompt_classificacao_vaga, prompt_sugestoes_seguras,
)
from app.services.selecao_evidencias import selecionar_evidencias_relevantes_para_vaga


ETAPAS = ["preparar_contexto_ia", "classificar_vaga", "selecionar_evidencias_relevantes",
          "avaliar_requisitos_contextualmente", "priorizar_lacunas",
          "gerar_sugestoes_seguras", "consolidar_resposta_ia"]

MENSAGENS_ERRO = {
    "timeout": "A etapa excedeu o tempo limite.", "rate_limit_429": "O provider limitou a etapa.",
    "request_too_large": "O contexto da etapa excedeu o limite.", "invalid_json": "A etapa retornou JSON inválido.",
    "json_truncated": "A etapa retornou JSON truncado.", "empty_response": "A etapa retornou resposta vazia.",
    "schema_validation_error": "A resposta não corresponde ao schema da etapa.",
    "unsupported_task_api": "O provider não implementa tarefas estruturadas.",
    "unknown_provider_error": "A etapa falhou e usou análise local.",
}


def _detalhe_fallback(etapa: str, provedor: ProvedorIA, schema: type, erro: Exception | None = None) -> dict:
    categoria = getattr(erro, "categoria", None) or ("unsupported_task_api" if erro is None else "unknown_provider_error")
    return {"etapa": etapa, "categoria_erro": categoria,
            "mensagem_segura": MENSAGENS_ERRO.get(categoria, MENSAGENS_ERRO["unknown_provider_error"]),
            "provider": provedor.nome, "modelo": provedor.modelo,
            "schema_usado": schema.__name__}


class RespostaAvaliacoes(BaseModel):
    avaliacoes: list[AvaliacaoContextualRequisito] = Field(default_factory=list)

    score_contextual_ia: int | None = Field(default=None, ge=0, le=100)
    confianca: int | None = Field(default=None, ge=0, le=100)


class RespostaSugestoes(BaseModel):

    sugestoes: list[str] = Field(default_factory=list)
    proximos_passos: list[str] = Field(default_factory=list)


def obter_politica_modelos_por_tarefa() -> dict[str, str]:
    """Formato opcional: classificacao_vaga=groq,avaliacao_contextual=openai."""
    politica = {"classificacao_vaga": "rapido", "avaliacao_contextual": "principal",
                "sugestoes_seguras": "principal", "fallback": "local"}
    for parte in os.getenv("IA_TASK_PROVIDER_POLICY", "").split(","):
        if "=" in parte:
            tarefa, perfil = (x.strip().lower() for x in parte.split("=", 1))
            if tarefa in politica and perfil:
                politica[tarefa] = perfil
    return politica


def preparar_contexto_ia(solicitacao: SolicitacaoAnalise, resultado: ResultadoAnalise) -> dict:
    contexto = montar_contexto_ia(solicitacao, resultado)
    # Fact Bank integral fica exclusivamente no processo local
    contexto.pop("fact_bank", None)
    return contexto


def _classificacao_local(resultado: ResultadoAnalise) -> ClassificacaoVagaIA:
    report = resultado.keyword_report
    centrais = [x.item for x in resultado.analise_por_requisito if x.peso >= 2]
    secundarios = [x.item for x in resultado.analise_por_requisito if x.peso < 2]
    return ClassificacaoVagaIA(
        titulo=str((resultado.avaliacao_relevancia or {}).get("titulo_detectado") or "") or None,
        senioridade=resultado.nivel_vaga, requisitos_centrais=centrais,
        requisitos_secundarios=secundarios,
        diferenciais=[x.item for x in resultado.analise_por_requisito if x.categoria == "diferencial"],
        hard_filters=[x.termo for x in report.hard_filters] if report else [],
        contexto_negocio=[x.termo for x in report.business_context] if report else [], confianca=75,
        empresa=(resultado.avaliacao_relevancia or {}).get("empresa") or None,
        area=(resultado.avaliacao_relevancia or {}).get("area") or None,
        tecnologias=[x.item for x in resultado.analise_por_requisito if x.tipo == "tecnologia"],
        responsabilidades=[], modalidade=(resultado.avaliacao_relevancia or {}).get("modalidade") or None,
        localizacao=(resultado.avaliacao_relevancia or {}).get("localizacao") or None,
        aceita_sem_experiencia=bool((resultado.avaliacao_relevancia or {}).get("aceita_sem_experiencia")),
    )


async def classificar_vaga(contexto: dict, resultado: ResultadoAnalise, provedor: ProvedorIA) -> tuple[ClassificacaoVagaIA, bool]:
    local = _classificacao_local(resultado)
    prompt = prompt_classificacao_vaga(contexto.get("resumo_vaga_sanitizado", ""), {
        "nivel": resultado.nivel_vaga, "requisitos": local.requisitos_centrais + local.requisitos_secundarios,
        "hard_filters": local.hard_filters}, ClassificacaoVagaIA.model_json_schema())
    try:
        bruto = await provedor.executar_tarefa_estruturada("classificacao_vaga", prompt, ClassificacaoVagaIA, 0.1)
        return (ClassificacaoVagaIA.model_validate(bruto), False, None) if bruto else (local, True, _detalhe_fallback("classificar_vaga", provedor, ClassificacaoVagaIA))
    except Exception as erro:
        return local, True, _detalhe_fallback("classificar_vaga", provedor, ClassificacaoVagaIA, erro)


def selecionar_evidencias_relevantes(resultado: ResultadoAnalise, classificacao: ClassificacaoVagaIA):
    return selecionar_evidencias_relevantes_para_vaga(
        resultado.fact_bank, resultado.analise_por_requisito, resultado.keyword_report,
        classificacao.senioridade or resultado.nivel_vaga)


def _avaliacoes_locais(resultado: ResultadoAnalise, evidencias: list) -> list[AvaliacaoContextualRequisito]:
    por_item = {}
    for evidencia in evidencias:
        por_item.setdefault(normalizar_para_comparacao(evidencia.item), evidencia)
    saida = []
    for item in resultado.analise_por_requisito:
        evidencia = por_item.get(normalizar_para_comparacao(item.item))
        ausente = item.status == "faltando"
        descricao = item.status in {"encontrado_sem_contexto_claro", "relacionado_mas_nao_explicito"}
        saida.append(AvaliacaoContextualRequisito(
            item=item.item, importancia="obrigatorio" if item.peso >= 3 else "desejavel",
            relevancia_para_vaga="alta" if item.peso >= 2 else "media", status=item.status,
            evidencia_usada=evidencia, lacuna_real=ausente, lacuna_de_descricao=descricao,
            recomendacao_segura=item.orientacao,
            risco_alucinacao="alto" if ausente else ("medio" if descricao else "baixo")))
    return saida


async def avaliar_requisitos_contextualmente(resultado: ResultadoAnalise, classificacao: ClassificacaoVagaIA,
                                              evidencias: list, provedor: ProvedorIA):

    locais = _avaliacoes_locais(resultado, evidencias)
    prompt = prompt_avaliacao_contextual(classificacao.model_dump(),
        [{"item": x.item, "peso": x.peso, "status_local": x.status} for x in resultado.analise_por_requisito],
        [x.model_dump() for x in evidencias], RespostaAvaliacoes.model_json_schema())

    try:
        bruto = await provedor.executar_tarefa_estruturada("avaliacao_contextual", prompt, RespostaAvaliacoes, 0.1)
        if not bruto:
            return locais, resultado.pontuacao_ats, 70, True, _detalhe_fallback("avaliar_requisitos_contextualmente", provedor, RespostaAvaliacoes)
        resposta = RespostaAvaliacoes.model_validate(bruto)


        # IA nunca pode elevar acima da evidência local
        externas = {normalizar_para_comparacao(x.item): x for x in resposta.avaliacoes}
        conciliadas = []
        for local in locais:
            externa = externas.get(normalizar_para_comparacao(local.item))
            if externa:
                local = local.model_copy(update={
                    "relevancia_para_vaga": externa.relevancia_para_vaga,
                    "recomendacao_segura": externa.recomendacao_segura or local.recomendacao_segura,
                    "risco_alucinacao": max(local.risco_alucinacao, externa.risco_alucinacao),
                })
            conciliadas.append(local)
        return conciliadas, resposta.score_contextual_ia or resultado.pontuacao_ats, resposta.confianca or 70, False, None
    except Exception as erro:
        return locais, resultado.pontuacao_ats, 60, True, _detalhe_fallback("avaliar_requisitos_contextualmente", provedor, RespostaAvaliacoes, erro)


def priorizar_lacunas(avaliacoes: list[AvaliacaoContextualRequisito]) -> list[dict]:
    prioridade = {"alta": 3, "media": 2, "baixa": 1}
    lacunas = [{"item": x.item, "prioridade": x.relevancia_para_vaga,
                "lacuna_real": x.lacuna_real, "lacuna_de_descricao": x.lacuna_de_descricao,
                "recomendacao": x.recomendacao_segura} for x in avaliacoes if x.lacuna_real or x.lacuna_de_descricao]
    return sorted(lacunas, key=lambda x: -prioridade.get(x["prioridade"], 0))


async def gerar_sugestoes_seguras(avaliacoes: list[AvaliacaoContextualRequisito], lacunas: list[dict], provedor: ProvedorIA):
    locais = list(dict.fromkeys(x.recomendacao_segura for x in avaliacoes if x.recomendacao_segura))[:12]
    prompt = prompt_sugestoes_seguras([x.model_dump() for x in avaliacoes], lacunas, RespostaSugestoes.model_json_schema())


    try:
        bruto = await provedor.executar_tarefa_estruturada("sugestoes_seguras", prompt, RespostaSugestoes, 0.1)
        if not bruto:
            return locais, [], True, _detalhe_fallback("gerar_sugestoes_seguras", provedor, RespostaSugestoes)
        resposta = RespostaSugestoes.model_validate(bruto)

        # Sugestões externas ainda passarão pela pós-validação local provada
        #
        #
        return resposta.sugestoes[:12], resposta.proximos_passos[:12], False, None
    except Exception as erro:
        return locais, [], True, _detalhe_fallback("gerar_sugestoes_seguras", provedor, RespostaSugestoes, erro)


def consolidar_resposta_ia(resultado: ResultadoAnalise, pipeline: ResultadoPipelineIA,
                           proximos_passos: list[str]) -> RespostaAnaliseIA:
    categoria = {"tecnologia": "habilidade_tecnica", "requisito": "outro"}
    requisitos = [AnaliseIARequisito(
        item=x.item, categoria=categoria.get(next((i.tipo for i in resultado.analise_por_requisito if i.item == x.item), "requisito"), "outro"),
        importancia=x.importancia if x.importancia in {"obrigatorio", "desejavel", "diferencial", "contextual", "nao_informado"} else "nao_informado",
        status=x.status if x.status in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro", "relacionado_mas_nao_explicito", "faltando", "nao_avaliado", "possivel_impeditivo"} else "nao_avaliado",
        evidencia=x.evidencia_usada.trecho if x.evidencia_usada else None,
        justificativa="Avaliação conciliada com evidência local selecionada.", recomendacao=x.recomendacao_segura or "Confirme a evidência antes de alterar o currículo.")
        for x in pipeline.avaliacao_requisitos]
    return RespostaAnaliseIA(
        resumo_contextual="Análise contextual em etapas, conciliada com evidências locais.",
        requisitos_contextuais=requisitos,
        pontos_fortes=[x.item for x in pipeline.avaliacao_requisitos if x.status == "encontrado_com_evidencia"],
        lacunas=[x.item for x in pipeline.avaliacao_requisitos if x.lacuna_real],
        possiveis_impeditivos=resultado.keyword_report.alertas_hard_filters if resultado.keyword_report else [],
        sugestoes_de_melhoria=pipeline.sugestoes_seguras, proximos_passos=proximos_passos,
        alertas_contra_inventar=["Não transforme curso, skill isolada ou tecnologia ausente em experiência prática."],
        confianca=pipeline.confianca_pipeline or 50, score_sugerido_ia=pipeline.score_contextual_ia,
        justificativa_score_ia="Score contextual calculado sobre requisitos e evidências selecionadas.",
        papel_ia=["classificadora da vaga", "auditora de evidências", "revisora anti-alucinação"],
        qualidade_contexto_ia=pipeline.confianca_pipeline,
        matriz_evidencia=[x.model_dump() for x in pipeline.evidencias_relevantes],
        lacunas_priorizadas=pipeline.lacunas_priorizadas,
        sugestoes_de_reescrita_seguras=pipeline.sugestoes_seguras,
        score_contextual_ia=pipeline.score_contextual_ia)


async def executar_pipeline_ia(solicitacao: SolicitacaoAnalise, resultado: ResultadoAnalise,
                               provedor: ProvedorIA) -> tuple[ResultadoPipelineIA, RespostaAnaliseIA]:
    executadas, fallbacks, detalhes = [], [], []
    contexto = preparar_contexto_ia(solicitacao, resultado); executadas.append(ETAPAS[0])
    classificacao, fallback, detalhe = await classificar_vaga(contexto, resultado, provedor); executadas.append(ETAPAS[1])
    if fallback: fallbacks.append(ETAPAS[1]); detalhes.append(detalhe)
    evidencias = selecionar_evidencias_relevantes(resultado, classificacao); executadas.append(ETAPAS[2])
    avaliacoes, score, confianca, fallback, detalhe = await avaliar_requisitos_contextualmente(resultado, classificacao, evidencias, provedor); executadas.append(ETAPAS[3])
    if fallback: fallbacks.append(ETAPAS[3]); detalhes.append(detalhe)
    lacunas = priorizar_lacunas(avaliacoes); executadas.append(ETAPAS[4])
    sugestoes, passos, fallback, detalhe = await gerar_sugestoes_seguras(avaliacoes, lacunas, provedor); executadas.append(ETAPAS[5])
    if fallback: fallbacks.append(ETAPAS[5]); detalhes.append(detalhe)
    confianca_pipeline = max(20, round(confianca - len(fallbacks) * 12))
    pipeline = ResultadoPipelineIA(classificacao_vaga=classificacao, evidencias_relevantes=evidencias,
        avaliacao_requisitos=avaliacoes, lacunas_priorizadas=lacunas, sugestoes_seguras=sugestoes,
        score_contextual_ia=score, confianca_pipeline=confianca_pipeline,
        etapas_executadas=executadas + [ETAPAS[6]], etapas_com_fallback=fallbacks,
        detalhes_fallback=[x for x in detalhes if x])
    return pipeline, consolidar_resposta_ia(resultado, pipeline, passos)
