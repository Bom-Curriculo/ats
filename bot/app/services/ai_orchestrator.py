import os

from pydantic import BaseModel, Field

from app.providers.base import AIProvider
from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.schemas.ai_pipeline import (
    ContextualRequirementEvaluation, AIJobClassification, AIPipelineResult,
)
from app.services.ai_context import build_ai_context
from app.services.text_normalizer import normalize_for_comparison
from app.services.ai_pipeline_prompts import (
    prompt_avaliacao_contextual, prompt_classificacao_vaga, prompt_sugestoes_seguras,
)
from app.services.evidence_selection import select_relevant_evidence_for_job


ETAPAS = ["prepare_ai_context", "classify_job", "select_relevant_evidence",
          "evaluate_requirements_contextually", "prioritize_gaps",
          "generate_safe_suggestions", "consolidate_ai_response"]

MENSAGENS_ERRO = {
    "timeout": "A etapa excedeu o tempo limite.", "rate_limit_429": "O provider limitou a etapa.",
    "request_too_large": "O contexto da etapa excedeu o limite.", "invalid_json": "A etapa retornou JSON inválido.",
    "json_truncated": "A etapa retornou JSON truncado.", "empty_response": "A etapa retornou resposta vazia.",
    "schema_validation_error": "A resposta não corresponde ao schema da etapa.",
    "unsupported_task_api": "O provider não implementa tarefas estruturadas.",
    "unknown_provider_error": "A etapa falhou e usou análise local.",
}


def _detalhe_fallback(etapa: str, provedor: AIProvider, schema: type, erro: Exception | None = None) -> dict:
    categoria = getattr(erro, "categoria", None) or ("unsupported_task_api" if erro is None else "unknown_provider_error")
    return {"etapa": etapa, "categoria_erro": categoria,
            "mensagem_segura": MENSAGENS_ERRO.get(categoria, MENSAGENS_ERRO["unknown_provider_error"]),
            "provider": provedor.nome, "modelo": provedor.modelo,
            "schema_usado": schema.__name__}


class EvaluationsResponse(BaseModel):
    avaliacoes: list[ContextualRequirementEvaluation] = Field(default_factory=list)

    score_contextual_ia: int | None = Field(default=None, ge=0, le=100)
    confianca: int | None = Field(default=None, ge=0, le=100)


class SuggestionsResponse(BaseModel):

    sugestoes: list[str] = Field(default_factory=list)
    proximos_passos: list[str] = Field(default_factory=list)


def get_task_model_policy() -> dict[str, str]:
    """Formato opcional: classificacao_vaga=groq,avaliacao_contextual=openai."""
    politica = {"classificacao_vaga": "rapido", "avaliacao_contextual": "principal",
                "sugestoes_seguras": "principal", "fallback": "local"}
    for parte in os.getenv("IA_TASK_PROVIDER_POLICY", "").split(","):
        if "=" in parte:
            tarefa, perfil = (x.strip().lower() for x in parte.split("=", 1))
            if tarefa in politica and perfil:
                politica[tarefa] = perfil
    return politica


def prepare_ai_context(solicitacao: AnalysisRequest, resultado: AnalysisResult) -> dict:
    contexto = build_ai_context(solicitacao, resultado)
    # Fact Bank integral fica exclusivamente no processo local
    contexto.pop("fact_bank", None)
    return contexto


def _classificacao_local(resultado: AnalysisResult) -> AIJobClassification:
    report = resultado.keyword_report
    centrais = [x.item for x in resultado.analise_por_requisito if x.peso >= 2]
    secundarios = [x.item for x in resultado.analise_por_requisito if x.peso < 2]
    return AIJobClassification(
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


async def classify_job(contexto: dict, resultado: AnalysisResult, provedor: AIProvider) -> tuple[AIJobClassification, bool]:
    local = _classificacao_local(resultado)
    prompt = prompt_classificacao_vaga(contexto.get("resumo_vaga_sanitizado", ""), {
        "nivel": resultado.nivel_vaga, "requisitos": local.requisitos_centrais + local.requisitos_secundarios,
        "hard_filters": local.hard_filters}, AIJobClassification.model_json_schema())
    try:
        bruto = await provedor.executar_tarefa_estruturada("classificacao_vaga", prompt, AIJobClassification, 0.1)
        return (AIJobClassification.model_validate(bruto), False, None) if bruto else (local, True, _detalhe_fallback("classify_job", provedor, AIJobClassification))
    except Exception as erro:
        return local, True, _detalhe_fallback("classify_job", provedor, AIJobClassification, erro)


def select_relevant_evidence(resultado: AnalysisResult, classificacao: AIJobClassification):
    return select_relevant_evidence_for_job(
        resultado.fact_bank, resultado.analise_por_requisito, resultado.keyword_report,
        classificacao.senioridade or resultado.nivel_vaga)


def _avaliacoes_locais(resultado: AnalysisResult, evidencias: list) -> list[ContextualRequirementEvaluation]:
    por_item = {}
    for evidencia in evidencias:
        por_item.setdefault(normalize_for_comparison(evidencia.item), evidencia)
    saida = []
    for item in resultado.analise_por_requisito:
        evidencia = por_item.get(normalize_for_comparison(item.item))
        ausente = item.status == "faltando"
        descricao = item.status in {"encontrado_sem_contexto_claro", "relacionado_mas_nao_explicito"}
        saida.append(ContextualRequirementEvaluation(
            item=item.item, importancia="obrigatorio" if item.peso >= 3 else "desejavel",
            relevancia_para_vaga="alta" if item.peso >= 2 else "media", status=item.status,
            evidencia_usada=evidencia, lacuna_real=ausente, lacuna_de_descricao=descricao,
            recomendacao_segura=item.orientacao,
            risco_alucinacao="alto" if ausente else ("medio" if descricao else "baixo")))
    return saida


async def evaluate_requirements_contextually(resultado: AnalysisResult, classificacao: AIJobClassification,
                                              evidencias: list, provedor: AIProvider):

    locais = _avaliacoes_locais(resultado, evidencias)
    prompt = prompt_avaliacao_contextual(classificacao.model_dump(),
        [{"item": x.item, "peso": x.peso, "status_local": x.status} for x in resultado.analise_por_requisito],
        [x.model_dump() for x in evidencias], EvaluationsResponse.model_json_schema())

    try:
        bruto = await provedor.executar_tarefa_estruturada("avaliacao_contextual", prompt, EvaluationsResponse, 0.1)
        if not bruto:
            return locais, resultado.pontuacao_ats, 70, True, _detalhe_fallback("evaluate_requirements_contextually", provedor, EvaluationsResponse)
        resposta = EvaluationsResponse.model_validate(bruto)


        # IA nunca pode elevar acima da evidência local
        externas = {normalize_for_comparison(x.item): x for x in resposta.avaliacoes}
        conciliadas = []
        for local in locais:
            externa = externas.get(normalize_for_comparison(local.item))
            if externa:
                local = local.model_copy(update={
                    "relevancia_para_vaga": externa.relevancia_para_vaga,
                    "recomendacao_segura": externa.recomendacao_segura or local.recomendacao_segura,
                    "risco_alucinacao": max(local.risco_alucinacao, externa.risco_alucinacao),
                })
            conciliadas.append(local)
        return conciliadas, resposta.score_contextual_ia or resultado.pontuacao_ats, resposta.confianca or 70, False, None
    except Exception as erro:
        return locais, resultado.pontuacao_ats, 60, True, _detalhe_fallback("evaluate_requirements_contextually", provedor, EvaluationsResponse, erro)


def prioritize_gaps(avaliacoes: list[ContextualRequirementEvaluation]) -> list[dict]:
    prioridade = {"alta": 3, "media": 2, "baixa": 1}
    lacunas = [{"item": x.item, "prioridade": x.relevancia_para_vaga,
                "lacuna_real": x.lacuna_real, "lacuna_de_descricao": x.lacuna_de_descricao,
                "recomendacao": x.recomendacao_segura} for x in avaliacoes if x.lacuna_real or x.lacuna_de_descricao]
    return sorted(lacunas, key=lambda x: -prioridade.get(x["prioridade"], 0))


async def generate_safe_suggestions(avaliacoes: list[ContextualRequirementEvaluation], lacunas: list[dict], provedor: AIProvider):
    locais = list(dict.fromkeys(x.recomendacao_segura for x in avaliacoes if x.recomendacao_segura))[:12]
    prompt = prompt_sugestoes_seguras([x.model_dump() for x in avaliacoes], lacunas, SuggestionsResponse.model_json_schema())


    try:
        bruto = await provedor.executar_tarefa_estruturada("sugestoes_seguras", prompt, SuggestionsResponse, 0.1)
        if not bruto:
            return locais, [], True, _detalhe_fallback("generate_safe_suggestions", provedor, SuggestionsResponse)
        resposta = SuggestionsResponse.model_validate(bruto)

        # Sugestões externas ainda passarão pela pós-validação local provada
        #
        #
        return resposta.sugestoes[:12], resposta.proximos_passos[:12], False, None
    except Exception as erro:
        return locais, [], True, _detalhe_fallback("generate_safe_suggestions", provedor, SuggestionsResponse, erro)


def consolidate_ai_response(resultado: AnalysisResult, pipeline: AIPipelineResult,
                           proximos_passos: list[str]) -> AIAnalysisResponse:
    categoria = {"tecnologia": "habilidade_tecnica", "requisito": "outro"}
    requisitos = [AIRequirementAnalysis(
        item=x.item, categoria=categoria.get(next((i.tipo for i in resultado.analise_por_requisito if i.item == x.item), "requisito"), "outro"),
        importancia=x.importancia if x.importancia in {"obrigatorio", "desejavel", "diferencial", "contextual", "nao_informado"} else "nao_informado",
        status=x.status if x.status in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro", "relacionado_mas_nao_explicito", "faltando", "nao_avaliado", "possivel_impeditivo"} else "nao_avaliado",
        evidencia=x.evidencia_usada.trecho if x.evidencia_usada else None,
        justificativa="Avaliação conciliada com evidência local selecionada.", recomendacao=x.recomendacao_segura or "Confirme a evidência antes de alterar o currículo.")
        for x in pipeline.avaliacao_requisitos]
    return AIAnalysisResponse(
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


async def run_ai_pipeline(solicitacao: AnalysisRequest, resultado: AnalysisResult,
                               provedor: AIProvider) -> tuple[AIPipelineResult, AIAnalysisResponse]:
    executadas, fallbacks, detalhes = [], [], []
    contexto = prepare_ai_context(solicitacao, resultado); executadas.append(ETAPAS[0])
    classificacao, fallback, detalhe = await classify_job(contexto, resultado, provedor); executadas.append(ETAPAS[1])
    if fallback: fallbacks.append(ETAPAS[1]); detalhes.append(detalhe)
    evidencias = select_relevant_evidence(resultado, classificacao); executadas.append(ETAPAS[2])
    avaliacoes, score, confianca, fallback, detalhe = await evaluate_requirements_contextually(resultado, classificacao, evidencias, provedor); executadas.append(ETAPAS[3])
    if fallback: fallbacks.append(ETAPAS[3]); detalhes.append(detalhe)
    lacunas = prioritize_gaps(avaliacoes); executadas.append(ETAPAS[4])
    sugestoes, passos, fallback, detalhe = await generate_safe_suggestions(avaliacoes, lacunas, provedor); executadas.append(ETAPAS[5])
    if fallback: fallbacks.append(ETAPAS[5]); detalhes.append(detalhe)
    confianca_pipeline = max(20, round(confianca - len(fallbacks) * 12))
    pipeline = AIPipelineResult(classificacao_vaga=classificacao, evidencias_relevantes=evidencias,
        avaliacao_requisitos=avaliacoes, lacunas_priorizadas=lacunas, sugestoes_seguras=sugestoes,
        score_contextual_ia=score, confianca_pipeline=confianca_pipeline,
        etapas_executadas=executadas + [ETAPAS[6]], etapas_com_fallback=fallbacks,
        detalhes_fallback=[x for x in detalhes if x])
    return pipeline, consolidate_ai_response(resultado, pipeline, passos)
