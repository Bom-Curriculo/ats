"""fact bank"""

from collections import Counter
import re

from app.schemas.analysis import FactBank
from app.services.technology_catalog import TECHNOLOGY_CATALOG
from app.services.technical_matching import contains_alias
from app.services.resume_entity_parser import section_block, extract_projects


# Technical note removed during English standardization.
SECTION_SOURCES = {
    "professional_experience": ("experiência profissional", "professional_experience"),
    "projects": ("project", "project"),
    "academic_projects": ("project acadêmico", "projeto_academico"),
    "freelance": ("freela", "freela"), "open_source": ("open source", "open_source"),
    "residencies": ("residência/laboratório prático", "technology_residency"),
    "courses": ("curso/formação", "curso_formacao"), "education": ("curso/formação", "curso_formacao"),
    "certifications": ("certificação", "certification"),
    "technical_skills": ("competências", "competencia"),
    "languages": ("languages", "language"), "achievements": ("conquista", "conquista"),
}


# Technical note removed during English standardization.
def _technologies(text: str) -> list[str]:
    return [t.name for t in TECHNOLOGY_CATALOG if contains_alias(text, t.aliases, t.name)]


def build_fact_bank(sections: dict[str, str]) -> FactBank:
    by_source: dict[str, list[str]] = {}
    evidence_items: list[dict] = []
    for section, (source, type) in SECTION_SOURCES.items():
        text = sections.get(section, "").strip()
        if not text:
            continue
        technologies = list(dict.fromkeys(_technologies(text)))
        by_source.setdefault(source, []).extend(technologies)

        # Implementation note.
        #
        real_delivery = bool(re.search(
            r"(?i)\b(entreg|cliente|publicad|deploy|contribu|commit|pull request|merged|aceit|implement|desenvolv|delivered|released|built|fixed)\w*\b",
            text,
        )) if type in {"freela", "open_source", "project"} else None
        for technology in technologies:
            aliases = next(t.aliases for t in TECHNOLOGY_CATALOG if t.name == technology)
            excerpt = next((line.strip() for line in text.splitlines() if contains_alias(line, aliases, technology)), "")
            evidence_items.append({"item": technology, "source": source, "source_type": type,
                               "evidence": excerpt[:500] or f"Detectado em {source}.",
                               "confidence": 90, "real_delivery": real_delivery, "secondary": False})


    # Technical note removed during English standardization.
    #
    unknown = sections.get("outros", "").strip()
    if unknown:
        technologies = _technologies(unknown)
        by_source["unknown"] = technologies
        for technology in technologies:
            evidence_items.append({"item": technology, "source": "unknown", "source_type": "unknown",
                               "evidence": "Technology detectada fora de seção confiável.", "confidence": 30,
                               "low_confidence": True, "reason": "Heading de origin não identificado.", "secondary": False})

    # Implementation note.
    #
    #
    #
    priority = {"professional_experience": 9, "freela": 8, "project": 7, "open_source": 6,
             "technology_residency": 5, "projeto_academico": 4, "curso_formacao": 3,
             "certification": 3, "competencia": 2, "language": 1, "conquista": 1}


    for item in {x["item"] for x in evidence_items}:
        candidates = [x for x in evidence_items if x["item"] == item]

        best = max(candidates, key=lambda x: priority.get(x["source_type"], 0))
        for evidence in candidates:
            evidence["secondary"] = evidence is not best

    projects = extract_projects(sections.get("projects", ""), source_type="project")
    academic_projects = extract_projects(sections.get("academic_projects", ""), source_type="projeto_academico")


    return FactBank(
        experiences=section_block(sections.get("professional_experience", ""), "professional_experience"),
        projects=projects,
        academic_projects=academic_projects,
        freelance=section_block(sections.get("freelance", ""), "freela"),
        open_source=section_block(sections.get("open_source", ""), "open_source"),

        residencies=section_block(sections.get("residencies", ""), "technology_residency"),
        courses=section_block(sections.get("courses", ""), "curso_formacao") + section_block(sections.get("education", ""), "curso_formacao"),
        certifications=section_block(sections.get("certifications", ""), "certification"),
        skills=section_block(sections.get("technical_skills", ""), "competencia"),
        languages=section_block(sections.get("languages", ""), "language"),

        achievements=section_block(sections.get("achievements", ""), "conquista"),
        technologies_by_source={k: list(dict.fromkeys(v)) for k, v in by_source.items()},
        evidence_items=evidence_items,
    )


# Technical note removed during English standardization.
def summarize_sources(fact_bank: FactBank) -> dict[str, int]:
    return dict(Counter(str(x.get("source_type", "unknown")) for x in fact_bank.evidence_items))
