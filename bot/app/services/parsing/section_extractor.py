import re

from app.services.normalization.text_normalizer import normalize_for_comparison, normalize_resume_text
from app.services.parsing.interfaces import SectionExtractorInterface, SectionParserResult

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

# Section-title confidence: exact match vs. a looser "starts with alias:" match.
EXACT_TITLE_MATCH_CONFIDENCE = 95
PARTIAL_TITLE_MATCH_CONFIDENCE = 90
# Fallback confidence when no heading was found at all, but the text still
# looks like a resume (or doesn't).
INFERRED_EXPERIENCE_CONFIDENCE = 45
NO_HEADINGS_CONFIDENCE = 25
# Confidence when headings exist but a suspiciously large amount of content
# fell outside any recognized section.
UNSECTIONED_CONTENT_CONFIDENCE = 35
UNSECTIONED_CONTENT_MIN_LENGTH = 120


class SectionExtractor(SectionExtractorInterface):
    """Bilingual (PT/EN) resume section extraction."""

    def _match_alias(self, alias_to_section: dict[str, str], title: str, comparison: str) -> str | None:
        # Match known aliases, longest first to avoid partial matches.
        return next(
            (a for a in sorted(alias_to_section, key=len, reverse=True) if title == a or comparison.startswith(a + ":")),
            None,
        )

    def _is_nested_stack_line(self, current_section: str, alias: str, line: str) -> bool:
        """A "Technologies:" line inside a projects section describes that project's stack, not a new top-level section."""
        return current_section in {"projects", "academic_projects"} and alias in {"tecnologias", "technologies", "tech stack"} and ":" in line

    def _classify_lines(self, lines: list[str]) -> tuple[dict[str, list[str]], dict[str, int], int]:
        alias_to_section = {alias: key for key, aliases in SECTION_ALIASES.items() for alias in aliases}
        sections: dict[str, list[str]] = {"outros": []}
        confidence: dict[str, int] = {}
        current_section = "outros"
        headings = 0

        for line in lines:
            comparison = normalize_for_comparison(line).strip()
            title = re.sub(r"[:\-–—]+$", "", comparison).strip()
            alias = self._match_alias(alias_to_section, title, comparison)

            if alias:
                if self._is_nested_stack_line(current_section, alias, line):
                    sections[current_section].append(line)
                    continue
                current_section = alias_to_section[alias]
                headings += 1
                sections.setdefault(current_section, [])
                confidence[current_section] = (
                    EXACT_TITLE_MATCH_CONFIDENCE if title == alias else PARTIAL_TITLE_MATCH_CONFIDENCE
                )
                remaining = line.split(":", 1)[1].strip() if ":" in line else ""
                if remaining:
                    sections[current_section].append(remaining)
                continue

            sections.setdefault(current_section, []).append(line)

        return sections, confidence, headings

    def _finalize_sections(self, sections: dict[str, list[str]]) -> dict[str, str]:
        return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}

    def _assess_low_confidence(
        self, output: dict[str, str], headings: int, confidence: dict[str, int]
    ) -> tuple[dict[str, str], list[str], list[str]]:
        warnings: list[str] = []
        low_confidence: list[str] = []

        if headings == 0:
            unsectioned = output.get("outros", "")
            if re.match(
                r"(?i)^\s*(?:experi[eê]ncia(?:\s+profissional)?|professional\s+experience|experience)\s+(?:com|em|with|in)\b",
                unsectioned,
            ):
                output = {"professional_experience": unsectioned}
                warnings.append("Experiência inferida por frase introdutória, sem heading explícito.")
                low_confidence.append("professional_experience")
                confidence["professional_experience"] = INFERRED_EXPERIENCE_CONFIDENCE
            else:
                warnings.append("Nenhum título de seção confiável foi identificado; conteúdo mantido como unknown.")
                low_confidence.append("outros")
                confidence["outros"] = NO_HEADINGS_CONFIDENCE
        elif output.get("outros") and len(output["outros"]) > UNSECTIONED_CONTENT_MIN_LENGTH:
            warnings.append("Há conteúdo relevante fora de seções reconhecidas.")
            low_confidence.append("outros")
            confidence["outros"] = UNSECTIONED_CONTENT_CONFIDENCE

        return output, warnings, low_confidence

    def analyze(self, text: str) -> SectionParserResult:
        lines = normalize_resume_text(text).splitlines()
        sections, confidence, headings = self._classify_lines(lines)
        output = self._finalize_sections(sections)
        output, warnings, low_confidence = self._assess_low_confidence(output, headings, confidence)
        return SectionParserResult(output, confidence, warnings, low_confidence)

    def extract_sections(self, text: str) -> dict[str, str]:
        """Legacy return shape containing only the section map."""
        return self.analyze(text).sections

    def detect_evidence(self, text: str, sections: dict[str, str]) -> dict[str, bool]:
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


def analyze_resume_sections(text: str) -> SectionParserResult:
    return SectionExtractor().analyze(text)


def extract_resume_sections(text: str) -> dict[str, str]:
    return SectionExtractor().extract_sections(text)


def detect_evidence(text: str, sections: dict[str, str]) -> dict[str, bool]:
    return SectionExtractor().detect_evidence(text, sections)
