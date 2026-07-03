
import asyncio

from app.providers.base import create_prompt
from app.providers.mock import MockProvider
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai, calculate_final_score


def analisar(cv: str, vaga: str):
    return analyze_resume(AnalysisRequest(curriculo_texto=cv, vaga_texto=vaga))


def test_keyword_report_pesa_hard_skill_e_lista_ausente():

    resultado = analisar("COMPETÊNCIAS\nPython", "Vaga backend\nPython, Docker e contexto financeiro")
    assert resultado.keyword_report is not None
    python = next(x for x in resultado.keyword_report.hard_skills if x.termo == "Python")
    docker = next(x for x in resultado.keywords_ausentes_ponderadas if x.termo == "Docker")
    assert python.peso == 2.0 and docker.peso == 2.0
    assert resultado.score_keyword_coverage is not None


def test_hard_filter_ausente_gera_alerta_forte():
    resultado = analisar("PROJETOS\nAPI em Python", "Obrigatório: graduação completa e Python")
    assert resultado.keyword_report.alertas_hard_filters
    assert any("hard filter" in x for x in resultado.alertas_score_final)


def test_fact_bank_separa_fontes_e_nao_promove_curso():
    resultado = analisar(
        "EXPERIÊNCIA PROFISSIONAL\nPython\nPROJETOS\nFastAPI e Docker\nCURSOS\nSpring Boot\nCOMPETÊNCIAS\nGit",
        "Python FastAPI Docker Spring Boot Git",
    )

    fb = resultado.fact_bank
    assert fb.experiencias and fb.projetos and fb.cursos and fb.skills
    assert "FastAPI" in fb.tecnologias_por_fonte["projeto"]
    assert "Docker" in fb.tecnologias_por_fonte["projeto"]

    assert "Spring Boot" in fb.tecnologias_por_fonte["curso/formação"]
    spring = next(x for x in resultado.analise_por_requisito if x.item == "Spring Boot")
    assert spring.nivel_evidencia == "evidencia_educacional"


def resposta_inventada():
    return {
        "resumo_contextual": "Análise.",
        "requisitos_contextuais": [{"item": "Kubernetes", "categoria": "ferramenta", "importancia": "obrigatorio", "status": "encontrado_com_evidencia", "evidencia": "Kubernetes em produção", "justificativa": "Consta.", "recomendacao": "Destaque."}],
        "pontos_fortes": ["Kubernetes"], "lacunas": [], "possiveis_impeditivos": [],
        "sugestoes_de_melhoria": ["Inclua Kubernetes na experiência."], "proximos_passos": [],
        "alertas_contra_inventar": [], "confianca": 95, "score_sugerido_ia": 95,
    }


def test_ia_inventando_evidencia_e_rebaixada_sem_provider_real():
    entrada = AnalysisRequest(curriculo_texto="PROJETOS\nDocker", vaga_texto="Kubernetes")

    resultado = asyncio.run(analyze_resume_with_ai(entrada, MockProvider(resposta_estruturada=resposta_inventada())))

    req = resultado.requisitos_contextuais[0]
    assert req.status == "faltando" and req.evidencia is None

    assert resultado.analise_ia.pontos_fortes == []
    assert any("Ponto forte sem evidência" in x for x in resultado.ajustes_validacao_ia)
    assert any("Estude ou crie um projeto" in x for x in resultado.proximos_passos)


def test_score_reduz_ia_com_muitas_correcoes_e_usa_keywords():
    poucos, _ = calculate_final_score(40, 100, 95, 0, "junior", False, 60)

    muitos, explicacao = calculate_final_score(40, 100, 95, 4, "junior", False, 60)

    sem_keywords, _ = calculate_final_score(40, 100, 95, 4, "junior", False, None)
    assert muitos < poucos and muitos != sem_keywords
    assert "correções 4" in explicacao


def test_contexto_do_prompt_e_compacto_rastreavel_e_sem_promover_skill():
    entrada = AnalysisRequest(curriculo_texto="COMPETÊNCIAS\nDocker", vaga_texto="Kubernetes")
    local = analyze_resume(entrada)
    prompt = create_prompt(entrada, local)


    assert '"fact_bank"' in prompt and "Skill solta nunca é prática" in prompt

    assert "Docker com Kubernetes" in prompt
