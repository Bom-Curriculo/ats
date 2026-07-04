import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.providers.base import AIProvider
from app.schemas.analysis import (
    DetailedAnalysis,
    ResumeEvidence,
    PrivacyInformation,
    RequirementAnalysisItem,
    AnalysisResult,
    AnalysisRequest,
    DetailedSuggestions,
)
from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.services.technology_catalog import TECHNOLOGY_CATALOG, Technology
from app.services.section_extractor import detect_evidence, extract_resume_sections, analyze_resume_sections
from app.services.resume_inventory import extract_resume_inventory
from app.services.fact_bank import build_fact_bank, summarize_sources
from app.services.keyword_report import build_keyword_report
from app.services.technical_matching import find_alias
from app.services.requirement_groups import build_requirement_groups
from app.services.ai_orchestrator import run_ai_pipeline
from app.services.text_normalizer import (
    normalize_for_comparison,
    normalize_resume_text,
)
from app.services.job_normalizer import clean_job_text, normalize_job_text
from app.services.privacy_sanitizer import sanitize_personal_data
from app.services.structured_ai_analysis import run_structured_ai_analysis
from app.services.technical_equivalences import (
    EvidenceLevel,
    JobLevel,
    detect_job_level,
    inferences_for,
    source_weight,
    public_status,
    SUBREQUIREMENT_GROUPS,
)

# Technical note removed during English standardization.
NON_TECHNICAL_REQUIREMENTS = (
    Technology("Inglês avançado", "languages", ("ingles avancado", "advanced english")),
    Technology(
        "graduação completa",
        "education",
        ("graduacao completa", "ensino superior complete"),
    ),
    Technology("portfólio", "ferramentas", ("portfolio",)),
)


# Technical note removed during English standardization.
EXPECTED_SECTIONS = {
    "experiência": "professional_experience",
    "formação": "education",
    "projects": "projects",
    "habilidades": "technical_skills",
}


@dataclass(frozen=True)
class Keyword:
    term: str

    weight: int

    priority: int

    grupo: str

    technology: bool


def normalize_text(text: str) -> str:

    return normalize_for_comparison(text)


# Technical note removed during English standardization.
def _ocorrencia(text: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    return find_alias(text, aliases)


def extract_job_requirements(
    job_estruturada: dict[str, str | list[str]],
) -> list[Keyword]:
    """Extract known catalog entries only from score-relevant areas."""

    requirements: dict[str, Keyword] = {}

    grupos = (
        ("requirement_obrigatorio", 3, "requirements_obrigatorios"),
        ("responsabilidade", 2, "responsibilities"),
        ("differential", 1, "differentials"),
    )

    catalogo = TECHNOLOGY_CATALOG + NON_TECHNICAL_REQUIREMENTS

    deslocamento = 0

    for grupo, weight, campo in grupos:
        value = job_estruturada.get(campo, [])

        text = normalize_for_comparison(
            "\n".join(value) if isinstance(value, list) else value
        )

        for technology in catalogo:
            match = _ocorrencia(text, technology.aliases)

            if match and technology.name not in requirements:
                requirements[technology.name] = Keyword(
                    technology.name,
                    weight,
                    deslocamento + match.start(),
                    grupo,
                    technology in TECHNOLOGY_CATALOG,
                )

        deslocamento += len(text) + 1

    # Technologies in the title are also primary requirements.
    title = normalize_for_comparison(str(job_estruturada.get("title", "")))

    for technology in TECHNOLOGY_CATALOG:
        match = _ocorrencia(title, technology.aliases)

        if match and technology.name not in requirements:
            requirements[technology.name] = Keyword(
                technology.name, 3, match.start(), "requirement_obrigatorio", True
            )

    # Implementation note.
    # Implementation note.
    text_completo = normalize_for_comparison(
        "\n".join(
            str(item)
            for value in job_estruturada.values()
            for item in (value if isinstance(value, list) else [value])
        )
    )
    for technology in catalogo:
        match = _ocorrencia(text_completo, technology.aliases)
        if match and technology.name not in requirements:
            requirements[technology.name] = Keyword(
                technology.name,
                1,
                deslocamento + match.start(),
                "context",
                technology in TECHNOLOGY_CATALOG,
            )

    # Technical note removed during English standardization.
    if ("APIs REST" in requirements or "APIs de IA" in requirements) and "APIs" in requirements:
        del requirements["APIs"]

    # Implementation note.
    pares_compostos = (
        ("Spring Boot", "Spring", r"\bspring\b(?!\s+boot)"),
        ("Docker Compose", "Docker", r"\bdocker\b(?!\s+compose)"),
        ("React Native", "React", r"\breact\b(?!\s+native)"),
    )
    for composto, base, standalone_base_pattern in pares_compostos:
        if composto in requirements and base in requirements and not re.search(standalone_base_pattern, text_completo):
            del requirements[base]

    return sorted(requirements.values(), key=lambda item: (-item.weight, item.priority))


def extract_weighted_relevant_keywords(
    text_job: str, limite: int = 40
) -> list[Keyword]:

    return extract_job_requirements(normalize_job_text(text_job))[:limite]


def extract_relevant_keywords(text_job: str, limite: int = 40) -> list[str]:

    return [
        item.term for item in extract_weighted_relevant_keywords(text_job, limite)
    ]


# Technical note removed during English standardization.
def _technology(name: str) -> Technology:

    return next(
        item for item in TECHNOLOGY_CATALOG + NON_TECHNICAL_REQUIREMENTS if item.name == name
    )


# Implementation note.
def _contains(text: str, name: str) -> bool:

    return (
        _ocorrencia(
            normalize_for_comparison(normalize_resume_text(text)),
            _technology(name).aliases,
        )
        is not None
    )


def detect_missing_sections(resume_text: str) -> list[str]:

    sections = extract_resume_sections(resume_text)

    return [
        f"Seção de {name} não identificada no currículo."
        for name, key in EXPECTED_SECTIONS.items()
        if key not in sections
    ]


def compare_resume_to_job(
    resume: str, sections: dict[str, str], requirements: list[Keyword]
) -> list[RequirementAnalysisItem]:
    """Classify each requirement without copying personal data."""

    items: list[RequirementAnalysisItem] = []

    sections_praticas_parciais = ("residencies", "academic_projects")
    sections_educacionais = ("education", "certifications", "courses")

    def contem_direto(text: str, name: str) -> bool:
        # Technical note removed during English standardization.
        # Implementation note.
        compostos = {
            "CSS": ("Tailwind CSS",),
            "Docker": ("Docker Compose",),
            "React": ("React Native",),
            "Spring": ("Spring Boot",),
        }
        limpo = text
        for composto in compostos.get(name, ()):
            limpo = re.sub(re.escape(composto), " ", limpo, flags=re.I)
        return _contains(limpo, name)

    def localizar(name: str) -> tuple[EvidenceLevel, str | None, str | None]:
        if contem_direto(sections.get("professional_experience", ""), name):
            return EvidenceLevel.STRONG_PRACTICAL, "experiência profissional", None
        freela = sections.get("freelance", "")
        if contem_direto(freela, name):
            entrega = re.search(r"\b(entreg|cliente|contrat|publicad|deploy|implement|desenvolv|delivered|client|contract|released|built)\w*\b", normalize_for_comparison(freela))
            return (EvidenceLevel.STRONG_PRACTICAL if entrega else EvidenceLevel.RELATED), "freela", None
        project = sections.get("projects", "")
        if contem_direto(project, name):
            return EvidenceLevel.STRONG_PRACTICAL, "project", None
        aberto = sections.get("open_source", "")
        if contem_direto(aberto, name):
            contribuicao = re.search(r"\b(contribu|commit|pull request|merged|aceit|corrig|implement|maintain|fixed)\w*\b", normalize_for_comparison(aberto))
            return (EvidenceLevel.STRONG_PRACTICAL if contribuicao else EvidenceLevel.RELATED), "open source", None
        if any(contem_direto(sections.get(s, ""), name) for s in sections_praticas_parciais):
            source = "residência/laboratório prático" if contem_direto(sections.get("residencies", ""), name) else "project acadêmico"
            return EvidenceLevel.PARTIAL_PRACTICAL, source, None
        if any(contem_direto(sections.get(s, ""), name) for s in sections_educacionais):
            return EvidenceLevel.EDUCATIONAL, "curso/formação", None
        for line in resume.splitlines():
            normalized_line = normalize_for_comparison(line)
            if contem_direto(line, name) and re.search(
                r"\b(curso|certifica|disciplina|formacao|bootcamp|treinamento)\b",
                normalized_line,
            ):
                return EvidenceLevel.EDUCATIONAL, "curso/formação", None
            if contem_direto(line, name) and re.search(
                r"\b(residencia tecnologica|laboratorio pratico|lab pratico)\b",
                normalized_line,
            ):
                return EvidenceLevel.PARTIAL_PRACTICAL, "residência/laboratório prático", None
        if contem_direto(sections.get("technical_skills", ""), name) or contem_direto(resume, name):
            return EvidenceLevel.STANDALONE_SKILL, "competências", None

        corpus = normalize_for_comparison(resume)
        for inference in inferences_for(name):
            try:
                origin_present = _contains(resume, inference.origin)
            except StopIteration:
                origin_present = normalize_for_comparison(inference.origin) in corpus
            context_ok = not inference.requires_context or any(
                term in corpus for term in inference.requires_context
            )
            if origin_present and context_ok:
                return EvidenceLevel.RELATED, inference.origin, inference.strength.value
        return EvidenceLevel.ABSENT, None, None

    for requirement in requirements:
        evidence_level, source, strength = localizar(requirement.term)
        status = public_status(evidence_level)
        evidence = (
            f"{requirement.term} aparece em {source}." if source and evidence_level != EvidenceLevel.RELATED
            else (f"{source} fornece evidência técnica relacionada, sem comprovar {requirement.term} diretamente." if source else None)
        )
        if evidence_level in {EvidenceLevel.STRONG_PRACTICAL, EvidenceLevel.PARTIAL_PRACTICAL}:
            guidance = "Mantenha a evidência objetiva e descreva uso, entrega e resultado alcançado."
        elif evidence_level == EvidenceLevel.EDUCATIONAL:
            guidance = "Mantenha como formação/conhecimento; associe a project real somente se essa aplicação existiu."
        elif evidence_level == EvidenceLevel.STANDALONE_SKILL:
            guidance = "Associe a habilidade a project ou experiência real, se possível."
        elif evidence_level == EvidenceLevel.RELATED:
            guidance = f"A relação com {source} é indício, não comprovação direta; explicite somente se tiver vivência real."
        else:
            guidance = f"Não inclua {requirement.term} como experiência se não tiver usado. Pode criar project prático para evidenciar."

        items.append(
            RequirementAnalysisItem(
                item=requirement.term,
                type="technology" if requirement.technology else "requirement",
                category=requirement.grupo,
                weight=requirement.weight,
                status=status,
                resume_evidence=evidence,
                guidance=guidance,
                evidence_level=evidence_level.value,
                evidence_source=source,
                inference_strength=strength,
            )
        )

    return items


def calculate_ats_score(
    items: list[RequirementAnalysisItem], valid_analysis: bool,
    job_level: JobLevel = JobLevel.NOT_PROVIDED,
) -> int:

    if not valid_analysis or not items:
        return 0

    grupos: dict[str, list[RequirementAnalysisItem]] = {}
    for item in items:
        key = next(
            (grupo for grupo, membros in SUBREQUIREMENT_GROUPS.items() if item.item in membros),
            item.item,
        )
        grupos.setdefault(key, []).append(item)
    total = sum(max(item.weight for item in grupo) for grupo in grupos.values())
    pontos = sum(
        max(item.weight for item in grupo)
        * max(source_weight(job_level, EvidenceLevel(item.evidence_level)) for item in grupo)
        for grupo in grupos.values()
    )
    score = round(pontos / total * 100)

    # Implementation note.
    return min(score, 95) if len(items) < 5 and score == 100 else score


def detect_possible_blockers(resume: str, job: str) -> list[str]:

    cv, descricao = (
        normalize_for_comparison(resume),
        normalize_for_comparison(clean_job_text(job)),
    )

    output: list[str] = []

    # Implementation note.
    if re.search(
        r"graduacao completa|ensino superior complete", descricao
    ) and re.search(r"graduacao.{0,40}cursando|cursando.{0,40}graduacao", cv):
        output.append(
            "Vaga pede graduação completa; currículo indica graduação em andamento."
        )

    # Implementation note.
    if (
        re.search(r"ingles avancado|advanced english", descricao)
        and "ingles tecnico" in cv
    ):
        output.append("Vaga pede inglês avançado; currículo indica inglês técnico.")

    # Implementation note.
    cidades = (
        "Manaus",
        "Recife",
        "São Paulo",
        "Rio de Janeiro",
        "Belo Horizonte",
        "Curitiba",
        "Porto Alegre",
        "Brasília",
        "Fortaleza",
        "Salvador",
    )

    # Implementation note.
    if re.search(r"\b(hibrid[oa]|presencial)\b", descricao):
        cidade_job = next(
            (c for c in cidades if normalize_for_comparison(c) in descricao), None
        )

        cidade_cv = next(
            (c for c in cidades if normalize_for_comparison(c) in cv), None
        )

        if cidade_job and cidade_cv and cidade_job != cidade_cv:
            output.append(
                f"Vaga é híbrida/presencial em {cidade_job}; currículo indica {cidade_cv}."
            )

    return output


def _is_valid_input(resume: str, job: str) -> tuple[bool, list[str]]:

    a, b = (
        normalize_for_comparison(resume),
        normalize_for_comparison(clean_job_text(job)),
    )

    similaridade = SequenceMatcher(None, a, b).ratio() if a and b else 0

    # Implementation note.
    if a == b or (min(len(a), len(b)) > 50 and similaridade >= 0.92):
        return False, [
            "Currículo e vaga são iguais ou muito parecidos; confirme os campos enviados."
        ]

    return True, []


def generate_local_suggestions(
    items: list[RequirementAnalysisItem],
    evidence_items: dict[str, bool],
    impeditivos: list[str],
    job: str,
) -> DetailedSuggestions:

    adjustments, gaps, atencao, passos = [], [], list(impeditivos), []

    # Implementation note.
    if not evidence_items["skills_section"]:
        adjustments.append(
            "Crie uma seção 'Competências Técnicas' claramente identificada; ela é fortemente recomendada para ATS tech, mas sua ausência não reprova automaticamente."
        )

    grupos_processados: set[str] = set()
    grupos = {
        "SQL": ({"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}, "SQL: consultas, JOINs, CRUD e modelagem"),
        "Git": ({"Git", "branches", "pull requests", "code review"}, "Git/versionamento: branches, pull requests e code review"),
        "Testes": ({"testes automatizados", "testes unitários", "testes de integração", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright"}, "testes automatizados: unitários, integração ou e2e"),
        "APIs": ({"APIs", "APIs REST", "Webhooks"}, "APIs REST e integrações: consumo, endpoints e webhooks"),
    }

    for item in items:
        grupo = next((name for name, (membros, _) in grupos.items() if item.item in membros), None)
        label = grupos[grupo][1] if grupo else item.item
        if grupo and grupo in grupos_processados:
            continue
        if grupo:
            grupos_processados.add(grupo)
        if item.status == "found_without_clear_context":
            adjustments.append(
                f"Detalhe best {label}, se você já usou em projects ou experiência."
            )

        elif item.status == "missing":
            gaps.append(
                f"Se não tiver experiência com {label}, trate como lacuna técnica da vaga."
            )

            passos.append(
                f"Considere estudar e criar um project prático com {label}, sem declarar experiência antes de utilizá-lo."
            )

        elif item.status == "related_but_not_explicit":
            adjustments.append(item.guidance)

    # Implementation note.
    if not evidence_items["professional_experience"]:
        passos.append(
            "Sem experiência profissional, evidencie projects pessoais ou acadêmicos, labs, freelance, residência tecnológica e courses práticos; isso não causa reprovação automática."
        )

    job_normalizada = normalize_for_comparison(job)

    if "portfolio" in job_normalizada and "portfólio" in [
        i.item for i in items if i.status == "missing"
    ]:
        passos.append(
            "Monte um portfólio com projects reais porque esta vaga o solicita."
        )

    adjustments = list(dict.fromkeys(adjustments))
    gaps = list(dict.fromkeys(gaps))
    passos = list(dict.fromkeys(passos))
    alerts_honestidade = ["Não inclua tecnologias, práticas ou resultados que você não possa comprovar."]
    return DetailedSuggestions(
        recommended_adjustments=adjustments,
        technical_gaps=gaps,
        attention_points=atencao,
        next_steps=passos,
        resume_adjustments=adjustments,
        real_gaps=gaps,
        study_next_steps=passos,
        anti_fabrication_alerts=alerts_honestidade,
    )


def _ai_requirement_key(name: str) -> str:
    key = normalize_for_comparison(name)
    equivalentes = {
        "html5": "html", "css3": "css", "api rest": "apis rest",
        "consumo de apis rest": "apis rest", "desenvolvimento de apis rest": "apis rest",
        "integracao de apis rest": "apis rest", "integracao de apis": "apis rest",
        "ingles": "ingles tecnico",
    }
    return normalize_for_comparison(equivalentes.get(name, equivalentes.get(key, key)))


def post_validate_ai_analysis(
    response: AIAnalysisResponse, local_result: AnalysisResult
) -> tuple[AIAnalysisResponse, list[str]]:
    """Reconcile external output with the traceable local inventory."""
    local_by_key = {_ai_requirement_key(i.item): i for i in local_result.requirement_analysis}
    adjustments: list[str] = []
    requirements: list[AIRequirementAnalysis] = []
    for req in response.contextual_requirements:
        key = _ai_requirement_key(req.item)
        local_item = local_by_key.get(key)
        if local_item and req.status != local_item.status:
            anterior = req.status
            req = req.model_copy(update={
                "status": local_item.status,
                "evidence": local_item.resume_evidence,
                "rationale": f"Classification reconciled with local evidence: {local_item.evidence_level}.",
            })
            label = req.item
            if local_item.evidence_level == EvidenceLevel.EDUCATIONAL.value:
                adjustments.append(f"{label} rebaixado para evidência educacional")
            elif anterior == "missing":
                adjustments.append(f"{label} corrigido por evidência ou equivalência local")
            else:
                adjustments.append(f"{label} conciliado com a força da evidência local")
        requirements.append(req)
    nao_gaps = {
        _ai_requirement_key(req.item)
        for req in requirements
        if req.status in {"found_with_evidence", "found_without_clear_context", "related_but_not_explicit"}
    }
    gaps = [item for item in response.gaps if _ai_requirement_key(item) not in nao_gaps]
    missing_items = {i.item for i in local_result.requirement_analysis if i.evidence_level == EvidenceLevel.ABSENT.value}
    strengths: list[str] = []
    for ponto in response.strengths:
        cited = [item for item in missing_items if normalize_for_comparison(item) in normalize_for_comparison(ponto)]
        if cited:
            adjustments.append(f"Ponto forte sem evidência removido: {', '.join(cited)}")
        else:
            strengths.append(ponto)
    melhorias, passos = [], list(response.next_steps)
    for suggestion in response.improvement_suggestions:
        cited = [item for item in missing_items if normalize_for_comparison(item) in normalize_for_comparison(suggestion)]
        if cited and re.search(r"\b(adicione|inclua|declare|destaque|reescreva)\b", normalize_for_comparison(suggestion)):
            passos.append(f"Estude ou crie um project real com {', '.join(cited)} antes de incluir como experiência.")
            adjustments.append(f"Sugestão sem evidência para {', '.join(cited)} movida para próximos passos")
        else:
            melhorias.append(suggestion)
    return response.model_copy(update={"contextual_requirements": requirements, "gaps": gaps,
        "strengths": strengths, "improvement_suggestions": melhorias,
        "next_steps": list(dict.fromkeys(passos))}), list(dict.fromkeys(adjustments))


def calculate_final_score(
    local: int, ia: int | None, confidence: int | None, adjustments: int,
    level: str, tem_experiencia: bool, keyword: int | None = None,
    hard_filters_ausentes: int = 0, qualidade_context: int | None = None,
    steps_fallback: int = 0,
) -> tuple[int, str]:
    if ia is None or (confidence or 0) < 70:
        base = round(local * .8 + keyword * .2) if keyword is not None else local
        return base, "A IA não apresentou confiança suficiente; prevaleceram score local e cobertura ponderada de keywords."
    weight_ia = .2 if adjustments >= 3 else .35
    if (qualidade_context or 100) < 60:
        weight_ia = min(weight_ia, .15)
    if steps_fallback:
        weight_ia = max(.05, weight_ia - min(.2, steps_fallback * .07))
    weight_keyword = .2 if keyword is not None else 0
    weight_local = 1 - weight_ia - weight_keyword
    final = round(local * weight_local + ia * weight_ia + (keyword or 0) * weight_keyword)
    if local < 50 and ia > 80:
        final = min(final, 75)
    if level in {JobLevel.MID_LEVEL.value, JobLevel.SENIOR.value} and not tem_experiencia:
        final = min(final, 65)
    if hard_filters_ausentes:
        final = min(final, max(35, 75 - hard_filters_ausentes * 10))
    return final, f"Conciliação explicável: local {round(weight_local*100)}%, keywords {round(weight_keyword*100)}% e IA {round(weight_ia*100)}%; confiança {confidence}%, correções {adjustments}, etapas com fallback {steps_fallback}, hard filters missing_items {hard_filters_ausentes}."


def analyze_resume(request: AnalysisRequest) -> AnalysisResult:
    """Run the pipeline without retaining source text."""

    resume_text_original = request.resume_text
    job_text_original = request.job_text
    resume_normalizado = normalize_resume_text(resume_text_original)
    job_normalizada = normalize_resume_text(job_text_original)
    sanitization_resume = sanitize_personal_data(resume_normalizado)
    sanitization_job = sanitize_personal_data(job_normalizada)
    urls_sources = "\n".join(source.url for source in request.resume_sources if source.url)
    sanitization_sources = sanitize_personal_data(urls_sources) if urls_sources else None
    resume_text_sanitized = sanitization_resume.text_sanitized
    job_text_sanitized = sanitization_job.text_sanitized

    job = normalize_job_text(job_text_sanitized)
    level_detectado = detect_job_level(job_text_original)
    try:
        job_level = JobLevel(normalize_for_comparison(request.job_level or "")) if request.job_level else level_detectado
    except ValueError:
        job_level = level_detectado

    parser_sections = analyze_resume_sections(resume_text_sanitized)
    sections = parser_sections.sections

    inventario = extract_resume_inventory(resume_text_sanitized, sections)
    fact_bank = build_fact_bank(sections)

    requirements = extract_job_requirements(job)
    items = compare_resume_to_job(resume_text_sanitized, sections, requirements)
    requirement_groups, score_agrupado, score_by_group = build_requirement_groups(items, job_level.value, job_text_sanitized)
    keyword_report, score_keywords, keywords_presentes, keywords_ausentes = build_keyword_report(
        items, job_text_sanitized, resume_text_sanitized, str(job.get("title", "")))
    valid_analysis, alerts = _is_valid_input(resume_text_sanitized, job_text_sanitized)
    impeditivos = detect_possible_blockers(resume_text_sanitized, job_text_sanitized)
    impeditivos.extend(keyword_report.hard_filter_alerts)
    evidence_items_dict = detect_evidence(resume_text_sanitized, sections)
    suggestions_det = generate_local_suggestions(
        items, evidence_items_dict, impeditivos, job_text_sanitized
    )

    found_items = [
        i.item
        for i in items
        if i.status in {"found_with_evidence", "found_without_clear_context"}
    ]

    missing_items = [
        i.item
        for i in items
        if i.status not in {"found_with_evidence", "found_without_clear_context"}
    ]

    inventario["habilidades_nao_exigidas_pela_job"] = [
        h
        for h in inventario["habilidades_detectadas"]
        if h not in {i.item for i in items}
    ]

    details = DetailedAnalysis(
        found_required_requirements=[
            i.item
            for i in items
            if i.category == "requirement_obrigatorio" and i.item in found_items
        ],
        missing_required_requirements=[
            i.item
            for i in items
            if i.category == "requirement_obrigatorio" and i.item in missing_items
        ],
        found_differentials=[
            i.item
            for i in items
            if i.category == "differential" and i.item in found_items
        ],
        missing_differentials=[
            i.item for i in items if i.category == "differential" and i.item in missing_items
        ],
        found_technologies=[
            i.item for i in items if i.type == "technology" and i.item in found_items
        ],
        missing_technologies=[
            i.item for i in items if i.type == "technology" and i.item in missing_items
        ],
        possible_blockers=impeditivos,
    )

    score = score_agrupado if valid_analysis else 0
    if parser_sections.sections_baixa_confidence and not any(
        key in sections for key in ("professional_experience", "projects", "academic_projects", "freelance", "open_source", "residencies")
    ):
        score = min(score, 70)

    issues = detect_missing_sections(resume_text_sanitized)
    job_longa_com_poucos_requirements = len(job_text_sanitized) >= 300 and len(items) < 3
    if job_longa_com_poucos_requirements:
        alert_extracao = "Poucos requisitos extraídos da vaga; a pontuação foi limitada por segurança."
        alerts.append(alert_extracao)
        issues.append(alert_extracao)
        score = min(score, 60)

    suggestions = (
        suggestions_det.recommended_adjustments
        + suggestions_det.technical_gaps
        + suggestions_det.attention_points
        + suggestions_det.next_steps
    )

    explanation = "O inventário lista todas as habilidades detectadas; o matching e o score usam somente requisitos reais desta vaga, ponderados por categoria e força da evidência."

    return AnalysisResult(
        valid_analysis=valid_analysis,
        input_alerts=alerts,
        ats_score=score,
        matched_keywords=found_items,
        missing_keywords=missing_items,
        resume_inventory=inventario,
        requirement_analysis=items,
        detailed_analysis=details,
        evidence_items=ResumeEvidence(**evidence_items_dict),
        detected_issues=issues,
        suggestions=suggestions,
        detailed_suggestions=suggestions_det,
        matching_explanation=explanation,
        generated_summary=f"Análise {'válida' if valid_analysis else 'inválida'}: {score}% de compatibilidade ponderada.",
        ai_provider="sem_ia",
        ai_model=None,
        job_level=job_level.value,
        keyword_report=keyword_report,
        score_keyword_coverage=score_keywords,
        weighted_present_keywords=keywords_presentes,
        weighted_missing_keywords=keywords_ausentes,
        keyword_coverage_explanation="Cobertura ponderada por categoria; hard filters geram alertas fora do score.",
        fact_bank=fact_bank,
        relevance_evaluation={"title_detectado": job.get("title", ""), "company": job.get("company", ""),
                              "area": job.get("area", ""), "level": job_level.value,
                              "modality": job.get("modality", ""), "location": job.get("localidade", ""),
                              "accepts_no_experience": bool(job.get("accepts_no_experience"))},
        evidence_matrix=[{"item": i.item, "source": i.evidence_source, "level": i.evidence_level} for i in items],
        prioritized_gaps=[{"item": i.item, "weight": i.weight} for i in items if i.status == "missing"],
        ats_diagnostics={"score_local": score, "score_keyword_coverage": score_keywords},
        final_score_factors={"score_local": score, "score_keyword_coverage": score_keywords},
        final_score_alerts=keyword_report.hard_filter_alerts,
        requirement_groups=requirement_groups,
        score_by_group=score_by_group,
        grouped_semantic_score=score_agrupado,
        parser_warnings=parser_sections.warnings,
        detected_sections=[x for x in sections if x != "outros"],
        low_confidence_sections=parser_sections.sections_baixa_confidence,
        evidence_source_summary=summarize_sources(fact_bank),
        sanitization_summary={
            "sensitive_data_detected": bool(sanitization_resume.items_removidos or (sanitization_sources and sanitization_sources.items_removidos)),
            "categories_removidas": list(dict.fromkeys(sanitization_resume.categories_removidas + (sanitization_sources.categories_removidas if sanitization_sources else []))),
            "quantidade_categories": len(set(sanitization_resume.categories_removidas + (sanitization_sources.categories_removidas if sanitization_sources else []))),
            "links_detectados_por_type": {key: sanitization_resume.links_detectados_por_type.get(key, 0) + (sanitization_sources.links_detectados_por_type.get(key, 0) if sanitization_sources else 0)
                                          for key in set(sanitization_resume.links_detectados_por_type) | set(sanitization_sources.links_detectados_por_type if sanitization_sources else {})},
            "observacao_safe": "Valores sensíveis foram substituídos antes da análise externa e não são retornados.",
        },
        recommended_final_score=score,
        final_score_explanation="Sem análise externa válida, o score final recomendado é igual à pontuação ATS local.",
    )


async def analyze_resume_with_ai(
    request: AnalysisRequest,
    provider: AIProvider,
    propagar_error_provider: bool = False,
) -> AnalysisResult:

    # roda primeiro
    result = analyze_resume(request)

    resume_sanitized = sanitize_personal_data(request.resume_text)
    job_sanitized = sanitize_personal_data(request.job_text)
    items = list(dict.fromkeys(resume_sanitized.items_removidos + job_sanitized.items_removidos))

    safe = request.model_copy(
        update={

            "resume_text": resume_sanitized.text_sanitized,
            "job_text": job_sanitized.text_sanitized,
            "resume_sources": [],
        }
    )



    ai_pipeline = None
    try:
        responses_tarefa = getattr(provider, "task_responses", None)
        suporta_pipeline = responses_tarefa is None or bool(responses_tarefa)
        if suporta_pipeline:
            ai_pipeline, ai_analysis = await run_ai_pipeline(safe, result, provider)
            if len(ai_pipeline.fallback_steps) >= 3:
                ai_analysis = await run_structured_ai_analysis(safe, result, provider)
        else:
            ai_analysis = await run_structured_ai_analysis(safe, result, provider)
    except Exception:


        if propagar_error_provider:
            raise

        ai_analysis = None

    if ai_analysis is None:
        return result.model_copy(
            update={
                "local_fallback_used": True,
                "recommended_final_score": result.ats_score,
                "final_score_explanation": "A IA falhou ou retornou schema inválido; foi mantida a pontuação ATS local.",
                "privacy": PrivacyInformation(
                    sensitive_data_detected=bool(items),
                    items_removed_before_ai=items,
                    ai_text_was_sanitized=True,
                ),
            }
        )

    ai_analysis, ajustes_validacao = post_validate_ai_analysis(ai_analysis, result)
    candidates = ai_analysis.improvement_suggestions + ai_analysis.next_steps
    suggestions_ia: list[str] = []
    vistas: set[str] = set()
    for suggestion in candidates:
        key = re.sub(r"\b(select|join|where|insert|update|delete|branches?|pull requests?|code review)\b", "grupo", normalize_for_comparison(suggestion))
        if key not in vistas:
            vistas.add(key)
            suggestions_ia.append(suggestion)
        if len(suggestions_ia) == 10:
            break
    score_final, explanation_final = calculate_final_score(
        result.ats_score,
        ai_analysis.ai_suggested_score,
        ai_analysis.confidence,
        len(ajustes_validacao),
        result.job_level,
        bool(result.evidence_items and result.evidence_items.professional_experience),
        result.score_keyword_coverage,
        len(result.keyword_report.hard_filter_alerts) if result.keyword_report else 0,
        ai_analysis.ai_context_quality,
        len(ai_pipeline.fallback_steps) if ai_pipeline else 0,
    )

    # Technical note removed during English standardization.
    return result.model_copy(
        update={
            "generated_summary": ai_analysis.contextual_summary,
            "suggestions": suggestions_ia or result.suggestions,
            "ai_provider": provider.name,
            "ai_model": provider.model,
            "ai_analysis": ai_analysis,
            "ai_suggested_score": ai_analysis.ai_suggested_score,
            "ai_score_rationale": ai_analysis.ai_score_rationale,
            "ai_confidence": ai_analysis.confidence,
            "local_fallback_used": False,
            "ai_validation_applied": True,
            "ai_validation_adjustments": ajustes_validacao,
            "recommended_final_score": score_final,
            "final_score_explanation": explanation_final,
            "contextual_requirements": ai_analysis.contextual_requirements,
            "contextual_gaps": ai_analysis.gaps,
            "next_steps": ai_analysis.next_steps,
            "anti_fabrication_alerts": ai_analysis.anti_fabrication_alerts,
            "ai_roles": ai_analysis.ai_roles or ["avaliadora contextual", "auditora de lacunas", "revisora anti-alucinação"],
            "ai_context_quality": ai_analysis.ai_context_quality,
            "relevance_evaluation": ai_analysis.relevance_evaluation or result.relevance_evaluation,
            "evidence_matrix": ai_analysis.evidence_matrix or result.evidence_matrix,
            "prioritized_gaps": ai_analysis.prioritized_gaps or result.prioritized_gaps,
            "safe_rewrite_suggestions": ai_analysis.safe_rewrite_suggestions,
            "ats_diagnostics": ai_analysis.ats_diagnostics or result.ats_diagnostics,
            "contextual_ai_score": ai_analysis.contextual_ai_score,
            "final_score_factors": {"score_local": result.ats_score, "score_keywords": result.score_keyword_coverage or 0,
                "score_ia": ai_analysis.ai_suggested_score or 0, "ai_confidence": ai_analysis.confidence,
                "correcoes_ia": len(ajustes_validacao), "fallback_steps": len(ai_pipeline.fallback_steps) if ai_pipeline else 0},
            "ai_pipeline": ai_pipeline,
            "executed_ai_steps": ai_pipeline.executed_steps if ai_pipeline else [],
            "fallback_ai_steps": ai_pipeline.fallback_steps if ai_pipeline else [],
            "job_relevant_evidence": ai_pipeline.relevant_evidence if ai_pipeline else [],
            "ai_job_classification": ai_pipeline.job_classification if ai_pipeline else None,
            "contextual_requirement_evaluations": ai_pipeline.requirement_evaluations if ai_pipeline else [],
            "ai_pipeline_confidence": ai_pipeline.pipeline_confidence if ai_pipeline else None,
            "sanitized_pipeline_errors": [x["safe_message"] for x in ai_pipeline.fallback_details] if ai_pipeline else [],
            "pipeline_fallback_details": ai_pipeline.fallback_details if ai_pipeline else [],
            "privacy": PrivacyInformation(
                sensitive_data_detected=bool(items),
                items_removed_before_ai=items,
                ai_text_was_sanitized=True,
            ),
        }
    )
