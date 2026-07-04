import pytest

from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume
from app.services.section_extractor import analyze_resume_sections, extract_resume_sections
from app.services.privacy_sanitizer import sanitize_personal_data


def analyze(cv: str, job: str = "Requisitos:\nPython"):
    return analyze_resume(AnalysisRequest(resume_text=cv, job_text=job, job_level="junior"))


def req(result, name):
    return next(x for x in result.requirement_analysis if x.item == name)


@pytest.mark.parametrize("heading,key", [
    ("Professional Summary", "professional_summary"), ("Work Experience", "professional_experience"),
    ("Featured Projects", "projects"), ("Academic Projects", "academic_projects"),
    ("Academic Background", "education"), ("Courses and Certifications", "certifications"),
    ("Technical Skills", "technical_skills"), ("Languages", "languages"),
    ("Achievements", "achievements"), ("Open Source Contributions", "open_source"),
])
def test_generic_fact_bank_parser_behavior_01(heading, key):
    assert key in extract_resume_sections(f"{heading}\nConteúdo")


def test_generic_fact_bank_parser_behavior_02():
    sections = extract_resume_sections(
        "CERTIFICAÇÕES\nCertificado Python\nCURSOS\nSpring Boot 40h\nPROJETOS\nProjeto Web\nStack: FastAPI\nCOMPETÊNCIAS\nDocker"
    )
    assert "Spring Boot" in sections["courses"] and "Spring Boot" not in sections.get("professional_experience", "")
    assert "Certificado" in sections["certifications"] and "Certificado" not in sections.get("professional_experience", "")
    assert "FastAPI" in sections["projects"] and "FastAPI" not in sections["technical_skills"]
    assert "Docker" in sections["technical_skills"] and "Docker" not in sections["projects"]


def test_generic_fact_bank_parser_behavior_03():
    result = analyze(
        "PROJETOS\nAplicação Desktop\nStack: C#, .NET 9, WPF\n- Implementado instalador e persistência\nServiço de Dados\nTecnologias: Python 3.12, FastAPI\n- Publicado endpoint com testes",
        "Requisitos:\nC#, .NET, Python e FastAPI",
    )
    assert len(result.fact_bank.projects) == 2
    assert result.fact_bank.projects[0]["name"] == "Aplicação Desktop"
    assert {"C#", ".NET"} <= set(result.fact_bank.projects[0]["technologies"])
    assert {"Python", "FastAPI"} <= set(result.fact_bank.projects[1]["technologies"])


def test_generic_fact_bank_parser_behavior_04():
    result = analyze("Python Docker pessoa interessada em desenvolvimento")
    assert result.low_confidence_sections == ["outros"]
    assert result.parser_warnings
    assert result.fact_bank.technologies_by_source["unknown"] == ["Python", "Docker"]


def test_generic_fact_bank_parser_behavior_05():
    cv = """RESIDÊNCIA TECNOLÓGICA
Laboratório orientado com Python e metodologias ágeis
FREELANCE
Entrega de API FastAPI publicada para cliente
OPEN SOURCE CONTRIBUTIONS
Contribuição aceita com testes em project Python
"""
    result = analyze(cv, "Requisitos:\nPython, FastAPI e metodologias ágeis")
    assert result.fact_bank.experiences == []
    assert result.fact_bank.residencies and result.fact_bank.freelance and result.fact_bank.open_source
    assert req(result, "FastAPI").evidence_source == "freela"
    assert req(result, "metodologias ágeis").evidence_source == "residência/laboratório prático"


def test_generic_fact_bank_parser_behavior_06():
    sem_entrega = analyze("FREELANCE\nConhecimento de FastAPI\nOPEN SOURCE\nInteresse em Python", "Requisitos:\nFastAPI e Python")
    assert req(sem_entrega, "FastAPI").status == "related_but_not_explicit"
    assert req(sem_entrega, "Python").status == "related_but_not_explicit"


def test_generic_fact_bank_parser_behavior_07():
    result = analyze("PROJETOS\nAPI Real\nStack: Python\n- Entrega publicada\nCURSOS\nPython 40h", "Requisitos:\nPython")
    assert req(result, "Python").evidence_source == "project"
    evidence_items = [x for x in result.fact_bank.evidence_items if x["item"] == "Python"]
    assert {x["source"] for x in evidence_items} == {"project", "curso/formação"}
    assert sum(not x["secondary"] for x in evidence_items) == 1


def test_generic_fact_bank_parser_behavior_08():
    course = analyze("CURSOS\nSpring Boot", "Requisitos:\nSpring Boot")
    skill = analyze("TECHNICAL SKILLS\nMetodologias ágeis", "Requisitos:\nMetodologias ágeis")
    assert req(course, "Spring Boot").evidence_level == "educational_evidence"
    assert req(skill, "metodologias ágeis").evidence_level == "standalone_skill_evidence"


@pytest.mark.parametrize("period", ["2020 - 2023", "Ago 2025 - Dez 2027", ".NET 9", "Java 17", "Python 3.12"])
def test_generic_fact_bank_parser_behavior_09(period):
    result = sanitize_personal_data(period)
    assert result.text_sanitized == period
    assert "telefone" not in result.items_removidos


def test_generic_fact_bank_parser_behavior_10():
    result = sanitize_personal_data("Contato: (81)99999-1234\nFormação: 2020 - 2023")
    assert "[TELEFONE_REMOVIDO]" in result.text_sanitized
    assert "2020 - 2023" in result.text_sanitized


def test_generic_fact_bank_parser_behavior_11():
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
    job = """Estágio em Desenvolvimento — aceita sem experiência
Requisitos: C#, Kotlin, .NET ou Spring Boot e metodologias ágeis
"""
    result = analyze(cv, job)
    assert len(result.fact_bank.projects) == 2
    assert req(result, "C#").evidence_source == "project"
    assert req(result, ".NET").evidence_source == "project"
    assert req(result, "Spring Boot").evidence_level == "educational_evidence"
    assert req(result, "Kotlin").status == "missing"
    assert result.fact_bank.certifications and not result.fact_bank.experiences
    assert any("2020 - 2023" in x["content"] for x in result.fact_bank.courses)
    assert result.recommended_final_score is not None


@pytest.mark.parametrize("cv,source", [
    ("WORK EXPERIENCE\nSoftware Intern\nBuilt a Python service", "experiência profissional"),
    ("ESTÁGIO\nDesenvolvimento de API Python para equipe interna", "experiência profissional"),
    ("ACADEMIC PROJECTS\nProject Analyzer\nStack: Python\n- Implemented data processing", "project acadêmico"),
    ("TECHNOLOGY RESIDENCY\nLaboratório prático orientado com Python", "residência/laboratório prático"),
])
def test_varied_sources_are_classified_without_specific_names(cv, source):
    result = analyze(cv, "Requisitos:\nPython")
    assert req(result, "Python").evidence_source == source
    if source != "experiência profissional":
        assert result.fact_bank.experiences == []


def test_generic_fact_bank_parser_behavior_13():
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
    result = analyze(cv, "Requirements:\nPython and Docker")
    assert result.fact_bank.projects
    assert req(result, "Python").evidence_source == "project"
    assert "2019 - 2023" in result.fact_bank.courses[0]["content"]


def test_generic_fact_bank_parser_behavior_14():
    result = analyze(
        "PROJECTS\nMobile Sample\nStack: Java\n- Built a prototype",
        """Mobile Internship — no experience required
Requirements:
Java or Kotlin
Differentials:
Spring Boot
""",
    )
    assert result.relevance_evaluation["accepts_no_experience"] is True
    alternativo = next(x for x in result.requirement_groups if x.mode == "any" and {"Java", "Kotlin"} <= set(x.items))
    assert alternativo.group_status == "atendido"
    assert req(result, "Kotlin").status == "missing"
    assert req(result, "Spring Boot").category == "differential"
