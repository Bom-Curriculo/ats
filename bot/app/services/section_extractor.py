
import re
from dataclasses import dataclass, field

from app.services.text_normalizer import normalize_for_comparison, normalize_resume_text

"""Bilingual resume section extraction."""
# Bilingual section-title variants found in resumes.
SECTION_ALIASES = {
    "professional_summary": ("resumo", "resumo profissional", "perfil profissional", "sobre mim", "summary", "professional summary", "profile"),
    "professional_experience": ("experiencia", "experiencia profissional", "historico profissional", "atuacao profissional", "estagios", "estagio", "work experience", "professional experience", "employment history", "internships", "internship experience"),
    "projects": ("projetos", "projetos de destaque", "projetos pessoais", "portfolio", "projects", "featured projects", "personal projects", "portfolio projects"),
    "academic_projects": ("projetos academic_projects", "project academico", "academic projects", "academic project", "university projects"),
    "education": ("educacao", "formacao", "formacao academica", "escolaridade", "education", "academic background"),
    "courses": ("cursos", "cursos complementares", "courses", "training", "professional development"),
    "certifications": ("certificacoes", "certificados", "certificacoes e cursos", "cursos e certificacoes", "certifications", "courses and certifications", "licenses", "licenses and certifications"),
    "technical_skills": ("competencias", "habilidades", "skills", "technical skills", "competencias tecnicas", "tecnologias", "tech stack", "core competencies"),
    "languages": ("idiomas", "languages"),
    "achievements": ("conquistas", "destaques", "premios", "reconhecimentos", "awards", "achievements", "honors"),
    "residencies": ("residencia tecnologica", "residencias tecnologicas", "technology residency", "technical residency"),
    "freelance": ("freelas", "freelance", "freelance work", "trabalhos autonomos", "projetos freelance"),
    "open_source": ("open source", "contribuicoes open source", "open source contributions"),
    "links_portfolio": ("links", "links e portfolio", "contato e links", "contact", "contact and links"),
}


@dataclass
class SectionParserResult:

    sections: dict[str, str]
    confidence_por_section: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    sections_baixa_confidence: list[str] = field(default_factory=list)


def analyze_resume_sections(text: str) -> SectionParserResult:
    lines = normalize_resume_text(text).splitlines()


    # Implementation note.
    alias_to_section = {alias: key for key, aliases in SECTION_ALIASES.items() for alias in aliases}
    sections: dict[str, list[str]] = {"outros": []}
    confidence: dict[str, int] = {}
    current_section = "outros"
    headings = 0

    for line in lines:
        comparison = normalize_for_comparison(line).strip()
        title = re.sub(r"[:\-–—]+$", "", comparison).strip()


        # Match known aliases, longest first to avoid partial matches.
        alias = next((a for a in sorted(alias_to_section, key=len, reverse=True)
                      if title == a or comparison.startswith(a + ":")), None)


        if alias:
            # Technical note removed during English standardization.
            #
            #
            # Technical note removed during English standardization.
            #
            #
            if current_section in {"projects", "academic_projects"} and alias in {"tecnologias", "technologies", "tech stack"} and ":" in line:
                sections[current_section].append(line)
                continue
            current_section = alias_to_section[alias]
            headings += 1
            sections.setdefault(current_section, [])
            confidence[current_section] = 95 if title == alias else 90
            remaining = line.split(":", 1)[1].strip() if ":" in line else ""
            if remaining:
                sections[current_section].append(remaining)
            continue
        sections.setdefault(current_section, []).append(line)

    output = {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


    warnings, low_confidence = [], []

    if headings == 0:
        unsectioned = output.get("outros", "")
        # Implementation note.
        if re.match(r"(?i)^\s*(?:experi[eê]ncia(?:\s+profissional)?|professional\s+experience|experience)\s+(?:com|em|with|in)\b", unsectioned):
            output = {"professional_experience": unsectioned}
            warnings.append("Experiência inferida por frase introdutória, sem heading explícito.")
            low_confidence.append("professional_experience")
            confidence["professional_experience"] = 45
        else:
            warnings.append("Nenhum título de seção confiável foi identificado; conteúdo mantido como unknown.")
            low_confidence.append("outros")
            confidence["outros"] = 25
    elif output.get("outros") and len(output["outros"]) > 120:
        warnings.append("Há conteúdo relevante fora de seções reconhecidas.")
        low_confidence.append("outros")
        confidence["outros"] = 35
    return SectionParserResult(output, confidence, warnings, low_confidence)


def extract_resume_sections(text: str) -> dict[str, str]:
    """Legacy return shape containing only the section map."""
    return analyze_resume_sections(text).sections


def detect_evidence(text: str, sections: dict[str, str]) -> dict[str, bool]:
    normalized = normalize_for_comparison(text)
    return {
        "professional_experience": bool(sections.get("professional_experience")),
        "personal_projects": bool(sections.get("projects")),
        "academic_projects": bool(sections.get("academic_projects")) or "project academico" in normalized,
        "open_source": bool(sections.get("open_source")) or bool(re.search(r"\bopen[ -]?source\b", normalized)),
        "courses": bool(sections.get("courses") or sections.get("certifications")),
        "technology_residency": bool(sections.get("residencies")) or "residencia tecnologica" in normalized,
        "skills_section": bool(sections.get("technical_skills")),
    }
