import pytest

from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume
from app.services.section_extractor import analyze_resume_sections, extract_resume_sections
from app.services.privacy_sanitizer import sanitize_personal_data


def analisar(cv: str, vaga: str = "Requisitos:\nPython"):
    return analyze_resume(AnalysisRequest(curriculo_texto=cv, vaga_texto=vaga, nivel_vaga="junior"))


def req(resultado, nome):
    return next(x for x in resultado.analise_por_requisito if x.item == nome)


@pytest.mark.parametrize("heading,chave", [
    ("Professional Summary", "resumo_profissional"), ("Work Experience", "experiencia_profissional"),
    ("Featured Projects", "projetos"), ("Academic Projects", "projetos_academicos"),
    ("Academic Background", "educacao"), ("Courses and Certifications", "certificacoes"),
    ("Technical Skills", "competencias_tecnicas"), ("Languages", "idiomas"),
    ("Achievements", "conquistas"), ("Open Source Contributions", "open_source"),
])
def test_parser_bilingue_reconhece_headings(heading, chave):
    assert chave in extract_resume_sections(f"{heading}\nConteúdo")


def test_curso_certificacao_projeto_e_skill_nao_migram_de_secao():
    secoes = extract_resume_sections(
        "CERTIFICAÇÕES\nCertificado Python\nCURSOS\nSpring Boot 40h\nPROJETOS\nProjeto Web\nStack: FastAPI\nCOMPETÊNCIAS\nDocker"
    )
    assert "Spring Boot" in secoes["cursos"] and "Spring Boot" not in secoes.get("experiencia_profissional", "")
    assert "Certificado" in secoes["certificacoes"] and "Certificado" not in secoes.get("experiencia_profissional", "")
    assert "FastAPI" in secoes["projetos"] and "FastAPI" not in secoes["competencias_tecnicas"]
    assert "Docker" in secoes["competencias_tecnicas"] and "Docker" not in secoes["projetos"]


def test_multiplos_projetos_extraidos_sem_nomes_hardcoded():
    resultado = analisar(
        "PROJETOS\nAplicação Desktop\nStack: C#, .NET 9, WPF\n- Implementado instalador e persistência\nServiço de Dados\nTecnologias: Python 3.12, FastAPI\n- Publicado endpoint com testes",
        "Requisitos:\nC#, .NET, Python e FastAPI",
    )
    assert len(resultado.fact_bank.projetos) == 2
    assert resultado.fact_bank.projetos[0]["nome"] == "Aplicação Desktop"
    assert {"C#", ".NET"} <= set(resultado.fact_bank.projetos[0]["tecnologias"])
    assert {"Python", "FastAPI"} <= set(resultado.fact_bank.projetos[1]["tecnologias"])


def test_sem_headings_e_conservador_e_observavel():
    resultado = analisar("Python Docker pessoa interessada em desenvolvimento")
    assert resultado.secoes_com_baixa_confianca == ["outros"]
    assert resultado.parser_warnings
    assert resultado.fact_bank.tecnologias_por_fonte["desconhecido"] == ["Python", "Docker"]


def test_fontes_especiais_nao_viram_emprego_formal():
    cv = """RESIDÊNCIA TECNOLÓGICA
Laboratório orientado com Python e metodologias ágeis
FREELANCE
Entrega de API FastAPI publicada para cliente
OPEN SOURCE CONTRIBUTIONS
Contribuição aceita com testes em projeto Python
"""
    resultado = analisar(cv, "Requisitos:\nPython, FastAPI e metodologias ágeis")
    assert resultado.fact_bank.experiencias == []
    assert resultado.fact_bank.residencias and resultado.fact_bank.freelas and resultado.fact_bank.open_source
    assert req(resultado, "FastAPI").fonte_evidencia == "freela"
    assert req(resultado, "metodologias ágeis").fonte_evidencia == "residência/laboratório prático"


def test_freela_e_open_source_exigem_sinal_de_entrega():
    sem_entrega = analisar("FREELANCE\nConhecimento de FastAPI\nOPEN SOURCE\nInteresse em Python", "Requisitos:\nFastAPI e Python")
    assert req(sem_entrega, "FastAPI").status == "relacionado_mas_nao_explicito"
    assert req(sem_entrega, "Python").status == "relacionado_mas_nao_explicito"


def test_projeto_vence_curso_e_fontes_secundarias_sao_preservadas():
    resultado = analisar("PROJETOS\nAPI Real\nStack: Python\n- Entrega publicada\nCURSOS\nPython 40h", "Requisitos:\nPython")
    assert req(resultado, "Python").fonte_evidencia == "projeto"
    evidencias = [x for x in resultado.fact_bank.evidencias if x["item"] == "Python"]
    assert {x["fonte"] for x in evidencias} == {"projeto", "curso/formação"}
    assert sum(not x["secundaria"] for x in evidencias) == 1


def test_curso_e_skill_isolados_mantem_forca_correta():
    curso = analisar("CURSOS\nSpring Boot", "Requisitos:\nSpring Boot")
    skill = analisar("TECHNICAL SKILLS\nMetodologias ágeis", "Requisitos:\nMetodologias ágeis")
    assert req(curso, "Spring Boot").nivel_evidencia == "evidencia_educacional"
    assert req(skill, "metodologias ágeis").nivel_evidencia == "evidencia_skill_solto"


@pytest.mark.parametrize("periodo", ["2020 - 2023", "Ago 2025 - Dez 2027", ".NET 9", "Java 17", "Python 3.12"])
def test_sanitizer_preserva_datas_e_versoes(periodo):
    resultado = sanitize_personal_data(periodo)
    assert resultado.texto_sanitizado == periodo
    assert "telefone" not in resultado.itens_removidos


def test_sanitizer_remove_telefone_real_e_preserva_periodo_no_mesmo_texto():
    resultado = sanitize_personal_data("Contato: (81)99999-1234\nFormação: 2020 - 2023")
    assert "[TELEFONE_REMOVIDO]" in resultado.texto_sanitizado
    assert "2020 - 2023" in resultado.texto_sanitizado


def test_regressao_anonimizada_parser_e_fontes():
    cv = """FORMAÇÃO
Technology em Sistemas | 2020 - 2023
PROJETOS
Aplicação Desktop
Stack: C#, .NET 9, WPF
- Desenvolvido instalador e banco local
Aplicação Web
Stack: JavaScript, HTML, CSS
- Publicada interface responsiva
CURSOS
Spring Boot e Java | 60h
CERTIFICAÇÕES
Certificação em fundamentos de cloud
Certificação em segurança de aplicações
COMPETÊNCIAS
Metodologias ágeis
"""
    vaga = """Estágio em Desenvolvimento — aceita sem experiência
Requisitos: C#, Kotlin, .NET ou Spring Boot e metodologias ágeis
"""
    resultado = analisar(cv, vaga)
    assert len(resultado.fact_bank.projetos) == 2
    assert req(resultado, "C#").fonte_evidencia == "projeto"
    assert req(resultado, ".NET").fonte_evidencia == "projeto"
    assert req(resultado, "Spring Boot").nivel_evidencia == "evidencia_educacional"
    assert req(resultado, "Kotlin").status == "faltando"
    assert resultado.fact_bank.certificacoes and not resultado.fact_bank.experiencias
    assert any("2020 - 2023" in x["conteudo"] for x in resultado.fact_bank.cursos)
    assert resultado.score_final_recomendado is not None


@pytest.mark.parametrize("cv,fonte", [
    ("WORK EXPERIENCE\nSoftware Intern\nBuilt a Python service", "experiência profissional"),
    ("ESTÁGIO\nDesenvolvimento de API Python para equipe interna", "experiência profissional"),
    ("ACADEMIC PROJECTS\nProject Analyzer\nStack: Python\n- Implemented data processing", "projeto acadêmico"),
    ("TECHNOLOGY RESIDENCY\nLaboratório prático orientado com Python", "residência/laboratório prático"),
])
def test_fontes_variadas_sao_classificadas_sem_nomes_especificos(cv, fonte):
    resultado = analisar(cv, "Requisitos:\nPython")
    assert req(resultado, "Python").fonte_evidencia == fonte
    if fonte != "experiência profissional":
        assert resultado.fact_bank.experiencias == []


def test_curriculo_pdf_like_com_secoes_fora_de_ordem():
    cv = """S K I L L S
Docker
L A N G U A G E S
English B2
P R O J E C T S
Automation Tool
Stack: Python, Docker
- Built and released a command line application
E D U C A T I O N
Computer Science | 2019 - 2023
"""
    resultado = analisar(cv, "Requirements:\nPython and Docker")
    assert resultado.fact_bank.projetos
    assert req(resultado, "Python").fonte_evidencia == "projeto"
    assert "2019 - 2023" in resultado.fact_bank.cursos[0]["conteudo"]


def test_vaga_estagio_sem_experiencia_e_alternativas_genericas():
    resultado = analisar(
        "PROJECTS\nMobile Sample\nStack: Java\n- Built a prototype",
        """Mobile Internship — no experience required
Requirements:
Java or Kotlin
Differentials:
Spring Boot
""",
    )
    assert resultado.avaliacao_relevancia["aceita_sem_experiencia"] is True
    alternativo = next(x for x in resultado.grupos_requisitos if x.modo == "any" and {"Java", "Kotlin"} <= set(x.itens))
    assert alternativo.status_grupo == "atendido"
    assert req(resultado, "Kotlin").status == "faltando"
    assert req(resultado, "Spring Boot").categoria == "diferencial"
