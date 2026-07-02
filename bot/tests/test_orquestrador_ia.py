import asyncio

from app.providers.base import ErroProvedorIA
from app.providers.mock import MockProvider
from app.schemas.analise import FactBank, ItemKeyword, KeywordReport, SolicitacaoAnalise
from app.services.analisador_ats import analisar_curriculo, analisar_curriculo_com_ia, calcular_score_final
from app.services.orquestrador_ia import executar_pipeline_ia, preparar_contexto_ia
from app.services.selecao_evidencias import selecionar_evidencias_relevantes_para_vaga


def entrada():
    return SolicitacaoAnalise(
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
    resultado = asyncio.run(analisar_curriculo_com_ia(solicitacao, provider))
    assert resultado.pipeline_ia is not None
    assert resultado.etapas_ia_executadas[-1] == "consolidar_resposta_ia"
    spring = next(x for x in resultado.avaliacao_contextual_requisitos if x.item == "Spring Boot")
    kube = next(x for x in resultado.avaliacao_contextual_requisitos if x.item == "Kubernetes")
    assert spring.status == "encontrado_sem_contexto_claro"
    assert spring.evidencia_usada.nivel_evidencia == "educacional"
    assert kube.status == "encontrado_sem_contexto_claro"
    assert kube.evidencia_usada.nivel_evidencia == "skill_solta"
    assert len(provider.prompts_tarefas) == 3


def test_falha_de_uma_etapa_continua_com_fallback_local():
    respostas = respostas_pipeline()
    respostas["avaliacao_contextual"] = ErroProvedorIA("falha", categoria="timeout")
    resultado = asyncio.run(analisar_curriculo_com_ia(entrada(), MockProvider(respostas_por_tarefa=respostas)))
    assert "avaliar_requisitos_contextualmente" in resultado.etapas_ia_com_fallback
    assert resultado.fallback_local_usado is False
    assert resultado.avaliacao_contextual_requisitos
    detalhe = next(x for x in resultado.detalhes_fallback_pipeline if x["etapa"] == "avaliar_requisitos_contextualmente")
    assert detalhe == {
        "etapa": "avaliar_requisitos_contextualmente", "categoria_erro": "timeout",
        "mensagem_segura": "A etapa excedeu o tempo limite.", "provider": "mock",
        "modelo": "modelo-mock", "schema_usado": "RespostaAvaliacoes",
    }
    assert resultado.erros_pipeline_ia_sanitizados == ["A etapa excedeu o tempo limite."]


def test_selecao_limita_sanitiza_e_nao_envia_fact_bank_inteiro():
    evidencias = [{"item": "Python", "fonte": "projeto", "evidencia": f"ana@example.com evidência {i} Python"} for i in range(40)]
    fb = FactBank(evidencias=evidencias)
    report = KeywordReport(hard_skills=[ItemKeyword(termo="Python", categoria="hard_skills", peso=2, presente=True)])
    selecionadas = selecionar_evidencias_relevantes_para_vaga(fb, ["Python"], report)
    assert len(selecionadas) <= 20
    assert all(len(x.trecho or "") <= 500 and "ana@example.com" not in (x.trecho or "") for x in selecionadas)

    local = analisar_curriculo(entrada())
    contexto = preparar_contexto_ia(entrada(), local)
    assert "fact_bank" not in contexto


def test_prompt_de_pipeline_contem_so_evidencias_selecionadas():
    provider = MockProvider(respostas_por_tarefa=respostas_pipeline())
    local = analisar_curriculo(entrada())
    asyncio.run(executar_pipeline_ia(entrada(), local, provider))
    prompts = "\n".join(p for _, p in provider.prompts_tarefas)
    assert '"evidencias_selecionadas"' in prompts
    assert '"tecnologias_por_fonte"' not in prompts
    assert "ana@example.com" not in prompts


def test_score_reduz_peso_ia_quando_pipeline_tem_fallback():
    completo, _ = calcular_score_final(40, 95, 90, 0, "junior", True, 50, 0, 90, 0)
    degradado, explicacao = calcular_score_final(40, 95, 90, 0, "junior", True, 50, 0, 90, 2)
    assert degradado < completo
    assert "etapas com fallback 2" in explicacao


def test_campos_antigos_permanecem_no_resultado_pipeline():
    resultado = asyncio.run(analisar_curriculo_com_ia(entrada(), MockProvider(respostas_por_tarefa=respostas_pipeline())))
    assert resultado.pontuacao_ats is not None
    assert resultado.palavras_chave_encontradas is not None
    assert resultado.score_final_recomendado is not None
    assert resultado.requisitos_contextuais is not None
