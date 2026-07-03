import asyncio

import pytest

from app.providers.mock import MockProvider
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai
from app.services.technical_equivalences import JobLevel, detect_job_level


def analisar(cv: str, vaga: str):
    return analyze_resume(AnalysisRequest(curriculo_texto=cv, vaga_texto=vaga))


@pytest.mark.parametrize(
    ("origem", "requisito"),
    [("Next.js", "React"), ("Spring Boot", "Java"), ("FastAPI", "Python"),
     ("Laravel", "PHP"), ("NestJS", "TypeScript"), ("ASP.NET Core", "C#"),
     ("Docker Compose", "Docker")],
)
def test_inferencias_fortes_nao_inventam_pratica(origem, requisito):
    resultado = analisar(f"COMPETÊNCIAS\n{origem}", f"Requisitos:\n{requisito}")
    item = resultado.analise_por_requisito[0]
    assert item.status == "relacionado_mas_nao_explicito"
    assert item.forca_inferencia == "implicacao_forte"


def test_html_e_css_cobrem_aliases_html5_css3():
    resultado = analisar("PROJETOS\nSite feito com HTML e CSS", "Requisitos:\nHTML5 e CSS3")
    assert {i.item: i.status for i in resultado.analise_por_requisito} == {
        "HTML": "encontrado_com_evidencia", "CSS": "encontrado_com_evidencia"
    }


def test_framework_em_curso_e_educacional_e_em_projeto_e_pratico():
    curso = analisar("CURSOS\nJava Moderno com Spring Boot", "Vaga júnior\nSpring Boot")
    projeto = analisar("PROJETOS\nAPI construída com Spring Boot", "Vaga júnior\nSpring Boot")
    assert curso.analise_por_requisito[0].nivel_evidencia == "evidencia_educacional"
    assert curso.analise_por_requisito[0].status == "encontrado_sem_contexto_claro"
    assert projeto.analise_por_requisito[0].status == "encontrado_com_evidencia"


def test_sql_subitens_nao_multiplicam_score_e_sugestoes():
    resultado = analisar(
        "COMPETÊNCIAS\nSQL", "Requisitos:\nSQL, SELECT, JOIN, WHERE, INSERT, UPDATE e DELETE"
    )
    assert all(i.status != "faltando" for i in resultado.analise_por_requisito)
    texto = " ".join(resultado.sugestoes).lower()
    assert texto.count("select") <= 1
    assert texto.count("join") <= 1


def test_inferencias_conservadoras():
    docker = analisar("PROJETOS\nDocker", "Requisitos:\nKubernetes")
    tailwind = analisar("PROJETOS\nTailwind", "Requisitos:\nCSS")
    chatgpt = analisar("Uso ChatGPT", "Requisitos:\nAPIs de IA")
    assert docker.analise_por_requisito[0].status == "faltando"
    assert tailwind.analise_por_requisito[0].status == "relacionado_mas_nao_explicito"
    assert chatgpt.analise_por_requisito[0].status == "faltando"


def test_api_de_ia_em_projeto_e_relacionada_sem_confundir_chatgpt_web():
    resultado = analisar("PROJETOS\nIntegração feita com OpenAI API", "Requisitos:\nAPIs de IA")
    item = next(i for i in resultado.analise_por_requisito if i.item == "APIs de IA")
    assert item.status == "relacionado_mas_nao_explicito"
    assert item.forca_inferencia == "implicacao_forte"


def test_idioma_reconhece_leitura_de_documentacao():
    resultado = analisar("IDIOMAS\nInglês para leitura de documentação", "Inglês técnico")
    assert resultado.analise_por_requisito[0].status != "faltando"


def test_nivel_e_peso_educacional_diferem():
    assert detect_job_level("Estágio em desenvolvimento") == JobLevel.ESTAGIO
    estagio = analisar("CURSOS\nSpring Boot", "Estágio\nSpring Boot")
    senior = analisar("CURSOS\nSpring Boot", "Desenvolvedor sênior\nSpring Boot")
    assert estagio.pontuacao_ats > senior.pontuacao_ats
    assert estagio.analise_valida is True


def test_nivel_pode_ser_informado_explicitamente():
    resultado = analyze_resume(AnalysisRequest(
        curriculo_texto="CURSOS\nSpring Boot", vaga_texto="Spring Boot", nivel_vaga="sênior"
    ))
    assert resultado.nivel_vaga == "senior"
    assert resultado.pontuacao_ats == 15


def resposta_ia(status_html="faltando", status_spring="encontrado_com_evidencia", score=90):
    def req(item, status):
        return {"item": item, "categoria": "habilidade_tecnica", "importancia": "obrigatorio",
                "status": status, "evidencia": item, "justificativa": "Avaliação externa.",
                "recomendacao": "Descreva apenas evidência real."}
    return {"resumo_contextual": "Análise concluída.",
            "requisitos_contextuais": [req("HTML5", status_html), req("Spring Boot", status_spring)],
            "pontos_fortes": [], "lacunas": ["HTML5"], "possiveis_impeditivos": [],
            "sugestoes_de_melhoria": ["Detalhe as tecnologias usadas."], "proximos_passos": [],
            "alertas_contra_inventar": ["Não invente."], "confianca": 95,
            "score_sugerido_ia": score, "justificativa_score_ia": "Boa aderência."}


def test_pos_validacao_corrige_equivalencia_e_rebaixa_curso():
    entrada = AnalysisRequest(
        curriculo_texto="PROJETOS\nSite com HTML\nCURSOS\nSpring Boot",
        vaga_texto="Vaga júnior\nHTML5 e Spring Boot",
    )
    resultado = asyncio.run(analyze_resume_with_ai(
        entrada, MockProvider(resposta_estruturada=resposta_ia())
    ))
    status = {i.item: i.status for i in resultado.requisitos_contextuais}
    assert status["HTML5"] == "encontrado_com_evidencia"
    assert status["Spring Boot"] == "encontrado_sem_contexto_claro"
    assert resultado.validacao_ia_aplicada is True
    assert len(resultado.ajustes_validacao_ia) == 2
    assert resultado.score_final_recomendado is not None
    assert resultado.explicacao_score_final


def test_fallback_mantem_score_local():
    entrada = AnalysisRequest(curriculo_texto="Python", vaga_texto="Python")
    resultado = asyncio.run(analyze_resume_with_ai(
        entrada, MockProvider(erro_simulado=RuntimeError("falha"))
    ))
    assert resultado.fallback_local_usado is True
    assert resultado.score_final_recomendado == resultado.pontuacao_ats
