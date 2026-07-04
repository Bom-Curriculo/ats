"""Tests for inventory, evidence, and early-career behavior."""

from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume
from app.services.parsing.section_extractor import extract_resume_sections
from app.services.matching.technology_catalog import Technology
from app.services.parsing.resume_inventory import extract_resume_inventory


# Technical note removed during English standardization.
def analyze(resume: str, job: str):

    return analyze_resume(
        AnalysisRequest(resume_text=resume, job_text=job)
    )


def test_realistic_ats_engine_behavior_01() -> None:

    result = analyze(
        "COMPETÊNCIAS TÉCNICAS\nJava, CSharp, DotNet, Python",
        "Requisitos:\nPython",
    )

    # Implementation note.
    assert {"Java", "C#"} <= set(result.resume_inventory["linguagens"])

    assert ".NET" in result.resume_inventory["backend"]

    # Implementation note.
    assert {"Java", "C#", ".NET"} <= set(
        result.resume_inventory["habilidades_nao_exigidas_pela_job"]
    )

    assert result.matched_keywords == ["Python"]


def test_realistic_ats_engine_behavior_02() -> None:

    result = analyze(
        "PROJETOS\nAPI construída com Node.js & Express.",
        "Requisitos:\nExpress.js",
    )

    # Technical note removed during English standardization.
    item = next(i for i in result.requirement_analysis if i.item == "Express.js")

    assert item.status == "found_with_evidence"


def test_realistic_ats_engine_behavior_03() -> None:

    result = analyze("COMPETÊNCIAS\nGitHub Actions", "Requisitos:\nGit")

    # Implementation note.
    item = next(i for i in result.requirement_analysis if i.item == "Git")

    assert item.status == "related_but_not_explicit"

    assert "Git" in result.missing_keywords


def test_realistic_ats_engine_behavior_04() -> None:

    result = analyze("COMPETÊNCIAS\nPython", "Requisitos:\nPython e FastAPI")

    # Technical note removed during English standardization.
    assert result.valid_analysis is True

    assert result.evidence_items.professional_experience is False

    # Technical note removed during English standardization.
    assert any(
        "projects pessoais" in text
        for text in result.detailed_suggestions.next_steps
    )

    # Implementation note.
    assert not any(
        "open source" in problema.lower() for problema in result.detected_issues
    )


def test_realistic_ats_engine_behavior_05() -> None:

    result = analyze("PROJETOS\nAPI com Python", "Requisitos:\nPython")

    # Technical note removed during English standardization.
    assert result.evidence_items.skills_section is False

    assert any(
        "fortemente recomendada" in text
        for text in result.detailed_suggestions.recommended_adjustments
    )


def test_realistic_ats_engine_behavior_06() -> None:

    sections = extract_resume_sections(
        "C O M P E T Ê N C I A S\nPython\nP R O J E T O S\nAPI"
    )

    assert sections["technical_skills"] == "Python"

    assert sections["projects"] == "API"


def test_realistic_ats_engine_behavior_07() -> None:
    job = """Getronics — Pessoa Desenvolvedora
Requisitos: Angular, React, HTML5, CSS3, JavaScript, TypeScript, APIs REST, Java e Spring Boot, Python com FastAPI ou Flask, MVC, integração de sistemas, tratamento de erros, SQL, SELECT, JOIN, WHERE, INSERT, UPDATE, DELETE e modelagem de banco de dados.
Desejáveis: Kubernetes, Docker, CI/CD, Git, branches, pull requests, code review, testes unitários, testes de integração, metodologias ágeis, inglês técnico, LLMs, APIs de IA e Prompt Engineering.
"""
    resume = """HABILIDADES
React, TypeScript, JavaScript, Python, FastAPI, SQL, Docker, Git e testes automatizados.
PROJETOS
API REST com Python, FastAPI, SQL, Docker, Git e testes automatizados.
"""

    result = analyze(resume, job)
    requirements = {item.item for item in result.requirement_analysis}

    assert len(requirements) >= 30
    assert {
        "React", "TypeScript", "JavaScript", "Python", "FastAPI",
        "SQL", "Docker", "Git", "testes unitários",
    } <= requirements
    assert {"Angular", "Spring Boot", "Kubernetes", "metodologias ágeis"} <= set(
        result.missing_keywords
    )
    assert not {
        "React", "TypeScript", "JavaScript", "Python", "FastAPI", "SQL", "Docker"
    } & set(result.resume_inventory["habilidades_nao_exigidas_pela_job"])


def test_realistic_ats_engine_behavior_08() -> None:
    job = "Requisitos:\nPython\n" + ("Descrição institucional sem competência técnica. " * 10)

    result = analyze("HABILIDADES\nPython", job)

    assert result.ats_score <= 60
    assert any("Poucos requisitos extraídos" in alert for alert in result.input_alerts)
    assert any("Poucos requisitos extraídos" in problema for problema in result.detected_issues)


def test_realistic_ats_engine_behavior_09() -> None:
    inventario = extract_resume_inventory(
        "HABILIDADES\nMetodologias ágeis, Python e LLMs"
    )
    keys_antigas = {
        "linguagens", "frontend", "backend", "mobile", "bancos_data",
        "devops", "cloud", "testes", "ferramentas", "metodologias",
        "languages", "education", "projetos_detectados", "habilidades_detectadas",
        "habilidades_nao_exigidas_pela_job",
    }

    assert "metodologias ágeis" in inventario["processos"]
    assert "LLMs" in inventario["ia"]
    assert {"metodologias ágeis", "Python", "LLMs"} <= set(
        inventario["habilidades_detectadas"]
    )
    assert keys_antigas <= inventario.keys()


def test_realistic_ats_engine_behavior_10(monkeypatch) -> None:
    import app.services.parsing.resume_inventory as modulo_inventario

    desconhecida = Technology("Competência futura", "category_futura", ("futuro",))
    monkeypatch.setattr(
        modulo_inventario, "TECHNOLOGY_CATALOG", modulo_inventario.TECHNOLOGY_CATALOG + (desconhecida,)
    )

    inventario = modulo_inventario.extract_resume_inventory("Projeto futuro")

    assert inventario["category_futura"] == ["Competência futura"]
    assert "Competência futura" in inventario["habilidades_detectadas"]
