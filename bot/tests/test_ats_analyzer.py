from app.models.analysis import AnalysisRequest
from app.services.ats_analyzer import (
    analyze_resume,
    detect_missing_sections,
    extract_relevant_keywords,
)


def test_ats_analyzer_behavior_01() -> None:

    request = AnalysisRequest(
        resume_text="Experiência com Python e APIs REST.",
        job_text="Desenvolvimento Python com FastAPI e Docker.",
    )

    result = analyze_resume(request)

    assert "Python" in result.matched_keywords
    assert "FastAPI" in result.missing_keywords

    assert "Docker" in result.missing_keywords
    assert 0 <= result.ats_score <= 100


def test_ats_analyzer_behavior_02() -> None:

    request = AnalysisRequest(
        resume_text="Python FastAPI Docker",
        job_text="Python FastAPI Docker",
    )

    result = analyze_resume(request)

    assert result.valid_analysis is False
    assert result.ats_score == 0
    assert result.input_alerts


def test_ats_analyzer_behavior_03() -> None:

    issues = detect_missing_sections("Experiência profissional com Python.")

    assert "Seção de experiência não identificada no currículo." not in issues

    assert "Seção de formação não identificada no currículo." in issues
    assert "Seção de projects não identificada no currículo." in issues


def test_ats_analyzer_behavior_04() -> None:

    palavras = extract_relevant_keywords("Qualificações user system React")
    assert "qualificacoes" not in palavras
    assert "user" not in palavras
    assert "system" not in palavras
    assert "React" in palavras


def test_ats_analyzer_behavior_05() -> None:

    palavras = extract_relevant_keywords(
        "Next.js, Tailwind CSS, Radix UI, shadcn/ui e design system"
    )

    assert {"Next.js", "Tailwind CSS", "Radix UI", "shadcn/ui", "design system"} <= set(
        palavras
    )


def test_requirements_required_weigh_more_than_differentials() -> None:

    result = analyze_resume(
        AnalysisRequest(
            resume_text="React",
            job_text="Requisitos obrigatórios:\nReact\nDiferenciais:\nFigma",
        )
    )

    assert result.ats_score == 56


def test_ats_analyzer_behavior_07() -> None:

    palavras = extract_relevant_keywords(
        "Job description via LinkedIn. Apply on Indeed. Glassdoor. 3 days ago. NestJS"
    )

    assert palavras == ["NestJS"]


def test_ats_analyzer_behavior_08() -> None:

    palavras = extract_relevant_keywords(
        "NestJS, AWS-SDK, Angular, Jest, Mocha, MongoDB e DynamoDB"
    )

    assert {
        "NestJS",
        "AWS-SDK",
        "Angular",
        "Jest",
        "Mocha",
        "MongoDB",
        "DynamoDB",
    } <= set(palavras)


def test_ats_analyzer_behavior_09() -> None:

    result = analyze_resume(
        AnalysisRequest(
            resume_text="Formação: graduação em Sistemas, cursando.",
            job_text="Requisitos obrigatórios:\nGraduação completa",
        )
    )

    assert (
        "Vaga pede graduação completa; currículo indica graduação em andamento."
        in result.detailed_analysis.possible_blockers
    )


def test_ats_analyzer_behavior_10() -> None:

    result = analyze_resume(
        AnalysisRequest(
            resume_text="Idiomas: inglês técnico.",
            job_text="Requisitos obrigatórios:\nInglês avançado",
        )
    )

    assert (
        "Vaga pede inglês avançado; currículo indica inglês técnico."
        in result.detailed_analysis.possible_blockers
    )


def test_ats_analyzer_behavior_11() -> None:

    result = analyze_resume(
        AnalysisRequest(
            resume_text="Localização: Recife.",
            job_text="Trabalho híbrido em Manaus. Requisitos: Python.",
        )
    )

    assert (
        "Vaga é híbrida/presencial em Manaus; currículo indica Recife."
        in result.detailed_analysis.possible_blockers
    )
