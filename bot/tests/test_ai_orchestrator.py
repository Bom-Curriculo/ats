import asyncio

from app.providers.base import AIProviderError
from app.providers.mock import MockProvider
from app.schemas.analysis import FactBank, ItemKeyword, KeywordReport, AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai, calculate_final_score
from app.services.ai_orchestrator import run_ai_pipeline, prepare_ai_context
from app.services.evidence_selection import select_relevant_evidence_for_job


def entrada():
    return AnalysisRequest(
        curriculo_texto="PROJETOS\nAPI FastAPI com Docker\nCURSOS\nSpring Boot\nCOMPETÊNCIAS\nKubernetes",
        vaga_texto="Vaga júnior backend: FastAPI, Docker, Spring Boot e Kubernetes",
    )


def respostas_pipeline():
    return {
        "classificacao_vaga": {"titulo": "Backend", "senioridade": "junior", "area": "software", "requisitos_centrais": ["FastAPI", "Docker"], "confianca": 90},
        "avaliacao_contextual": {"avaliacoes": [
            {"item": "Spring Boot", "status": "encontrado_com_evidencia", "evidencia_usada": {"item": "Spring Boot", "fonte": "curso/formação", "nivel_evidencia": "pratica_forte"}, "lacuna_real": False, "lacuna_de_descricao": False, "recomendacao_segura": "Declare experiência forte.", "risco_alucinacao": "alto"}
        ], "score_contextual_ia": 88, "confianca": 90},
        "sugestoes_seguras": {"sugestoes": ["Detalhe apenas usos comprovados."], "proximos_passos": []},
    }


def test_pipeline_funciona_com_mock_e_preserva_gate_local():
    solicitacao = entrada()
    provider = MockProvider(respostas_por_tarefa=respostas_pipeline())
    resultado = asyncio.run(analyze_resume_with_ai(solicitacao, provider))
    assert resultado.pipeline_ia is not None
    assert resultado.etapas_ia_executadas[-1] == "consolidate_ai_response"
    spring = next(x for x in resultado.avaliacao_contextual_requisitos if x.item == "Spring Boot")
    kube = next(x for x in resultado.avaliacao_contextual_requisitos if x.item == "Kubernetes")
    assert spring.status == "encontrado_sem_contexto_claro"
    assert spring.evidencia_usada.nivel_evidencia == "educacional"
    assert kube.status == "encontrado_sem_contexto_claro"
    assert kube.evidencia_usada.nivel_evidencia == "skill_solta"
    assert len(provider.prompts_tarefas) == 3


def test_failure_de_uma_etapa_continua_com_fallback_local():
    respostas = respostas_pipeline()
    respostas["avaliacao_contextual"] = AIProviderError("falha", categoria="timeout")
    resultado = asyncio.run(analyze_resume_with_ai(entrada(), MockProvider(respostas_por_tarefa=respostas)))
    assert "evaluate_requirements_contextually" in resultado.etapas_ia_com_fallback
    assert resultado.fallback_local_usado is False
    assert resultado.avaliacao_contextual_requisitos
    detalhe = next(x for x in resultado.detalhes_fallback_pipeline if x["etapa"] == "evaluate_requirements_contextually")
    assert detalhe == {
        "etapa": "evaluate_requirements_contextually", "categoria_erro": "timeout",
        "mensagem_segura": "A etapa excedeu o tempo limite.", "provider": "mock",
        "modelo": "modelo-mock", "schema_usado": "EvaluationsResponse",
    }
    assert resultado.erros_pipeline_ia_sanitizados == ["A etapa excedeu o tempo limite."]


def test_selecao_limita_sanitiza_e_nao_envia_fact_bank_inteiro():
    evidencias = [{"item": "Python", "fonte": "projeto", "evidencia": f"ana@example.com evidência {i} Python"} for i in range(40)]
    fb = FactBank(evidencias=evidencias)
    report = KeywordReport(hard_skills=[ItemKeyword(termo="Python", categoria="hard_skills", peso=2, presente=True)])
    selecionadas = select_relevant_evidence_for_job(fb, ["Python"], report)
    assert len(selecionadas) <= 20
    assert all(len(x.trecho or "") <= 500 and "ana@example.com" not in (x.trecho or "") for x in selecionadas)

    local = analyze_resume(entrada())
    contexto = prepare_ai_context(entrada(), local)
    assert "fact_bank" not in contexto


def test_prompt_de_pipeline_contains_so_evidencias_selecionadas():
    provider = MockProvider(respostas_por_tarefa=respostas_pipeline())
    local = analyze_resume(entrada())
    asyncio.run(run_ai_pipeline(entrada(), local, provider))
    prompts = "\n".join(p for _, p in provider.prompts_tarefas)
    assert '"evidencias_selecionadas"' in prompts
    assert '"tecnologias_por_fonte"' not in prompts
    assert "ana@example.com" not in prompts


def test_score_reduz_peso_ia_quando_pipeline_tem_fallback():
    completo, _ = calculate_final_score(40, 95, 90, 0, "junior", True, 50, 0, 90, 0)
    degradado, explicacao = calculate_final_score(40, 95, 90, 0, "junior", True, 50, 0, 90, 2)
    assert degradado < completo
    assert "etapas com fallback 2" in explicacao


def test_campos_antigos_permanecem_no_resultado_pipeline():
    resultado = asyncio.run(analyze_resume_with_ai(entrada(), MockProvider(respostas_por_tarefa=respostas_pipeline())))
    assert resultado.pontuacao_ats is not None
    assert resultado.palavras_chave_encontradas is not None
    assert resultado.score_final_recomendado is not None
    assert resultado.requisitos_contextuais is not None
