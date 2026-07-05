import re
from dataclasses import dataclass

from app.models.analysis import RequirementAnalysisItem
from app.services.analysis.interfaces import RequirementExtractorInterface
from app.services.matching.technology_catalog import TECHNOLOGY_CATALOG, Technology
from app.services.matching.technical_matching import find_alias
from app.services.matching.technical_equivalences import EvidenceLevel, inferences_for, public_status
from app.services.normalization.text_normalizer import normalize_for_comparison, normalize_resume_text
from app.services.normalization.job_normalizer import normalize_job_text
from app.services.parsing.section_extractor import extract_resume_sections

NON_TECHNICAL_REQUIREMENTS = (
    Technology("Inglês avançado", "languages", ("ingles avancado", "advanced english")),
    Technology(
        "graduação completa",
        "education",
        ("graduacao completa", "ensino superior complete"),
    ),
    Technology("portfólio", "ferramentas", ("portfolio",)),
)

EXPECTED_SECTIONS = {
    "experiência": "professional_experience",
    "formação": "education",
    "projects": "projects",
    "habilidades": "technical_skills",
}

# Requirement weight by where it was found in the job post.
REQUIRED_WEIGHT = 3
RESPONSIBILITY_WEIGHT = 2
DIFFERENTIAL_WEIGHT = 1
CONTEXT_WEIGHT = 1

_WEIGHTED_JOB_SECTIONS = (
    ("requirement_obrigatorio", REQUIRED_WEIGHT, "requirements_obrigatorios"),
    ("responsabilidade", RESPONSIBILITY_WEIGHT, "responsibilities"),
    ("differential", DIFFERENTIAL_WEIGHT, "differentials"),
)

# Drop the generic base term when its compound form is present and the base
# doesn't also appear standalone (e.g. "Spring Boot" implies "Spring" was
# matched only because "Spring Boot" contains "spring").
_COMPOUND_TERM_PAIRS = (
    ("Spring Boot", "Spring", r"\bspring\b(?!\s+boot)"),
    ("Docker Compose", "Docker", r"\bdocker\b(?!\s+compose)"),
    ("React Native", "React", r"\breact\b(?!\s+native)"),
)

# Strip a compound term's occurrences before checking a plain base term, so
# e.g. "Docker Compose" doesn't get counted as direct evidence for "Docker".
_COMPOUND_TERM_STRIP_MAP = {
    "CSS": ("Tailwind CSS",),
    "Docker": ("Docker Compose",),
    "React": ("React Native",),
    "Spring": ("Spring Boot",),
}

_PARTIAL_PRACTICAL_SECTIONS = ("residencies", "academic_projects")
_EDUCATIONAL_SECTIONS = ("education", "certifications", "courses")


@dataclass(frozen=True)
class Keyword:
    term: str
    weight: int
    priority: int
    grupo: str
    technology: bool


def normalize_text(text: str) -> str:
    return normalize_for_comparison(text)


class RequirementExtractor(RequirementExtractorInterface):
    """Extract a job's requirements from the catalog and match them against a resume."""

    def _find_occurrence(self, text: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
        return find_alias(text, aliases)

    def _technology(self, name: str) -> Technology:
        return next(
            item for item in TECHNOLOGY_CATALOG + NON_TECHNICAL_REQUIREMENTS if item.name == name
        )

    def _contains(self, text: str, name: str) -> bool:
        return (
            self._find_occurrence(
                normalize_for_comparison(normalize_resume_text(text)),
                self._technology(name).aliases,
            )
            is not None
        )

    def _match_catalog(
        self,
        text: str,
        catalog: tuple[Technology, ...],
        requirements: dict[str, Keyword],
        group: str,
        weight: int,
        offset: int,
    ) -> None:
        for technology in catalog:
            match = self._find_occurrence(text, technology.aliases)
            if match and technology.name not in requirements:
                requirements[technology.name] = Keyword(
                    technology.name, weight, offset + match.start(), group, technology in TECHNOLOGY_CATALOG,
                )

    def _add_matches_from_weighted_sections(
        self, job_estruturada: dict[str, str | list[str]], requirements: dict[str, Keyword]
    ) -> int:
        """Match catalog entries from the weighted job sections; return the text length scanned so far."""
        offset = 0
        catalog = TECHNOLOGY_CATALOG + NON_TECHNICAL_REQUIREMENTS
        for group, weight, field in _WEIGHTED_JOB_SECTIONS:
            value = job_estruturada.get(field, [])
            text = normalize_for_comparison("\n".join(value) if isinstance(value, list) else value)
            self._match_catalog(text, catalog, requirements, group, weight, offset)
            offset += len(text) + 1
        return offset

    def _add_matches_from_title(
        self, job_estruturada: dict[str, str | list[str]], requirements: dict[str, Keyword]
    ) -> None:
        """Technologies in the title are also primary requirements."""
        title = normalize_for_comparison(str(job_estruturada.get("title", "")))
        self._match_catalog(title, TECHNOLOGY_CATALOG, requirements, "requirement_obrigatorio", REQUIRED_WEIGHT, 0)

    def _add_context_matches(
        self, job_estruturada: dict[str, str | list[str]], requirements: dict[str, Keyword], offset: int
    ) -> str:
        """Anything else mentioned anywhere in the job post is weak (context) signal."""
        full_text = normalize_for_comparison(
            "\n".join(
                str(item)
                for value in job_estruturada.values()
                for item in (value if isinstance(value, list) else [value])
            )
        )
        catalog = TECHNOLOGY_CATALOG + NON_TECHNICAL_REQUIREMENTS
        self._match_catalog(full_text, catalog, requirements, "context", CONTEXT_WEIGHT, offset)
        return full_text

    def _remove_redundant_generic_apis(self, requirements: dict[str, Keyword]) -> None:
        """"APIs REST"/"APIs de IA" are more specific than the generic "APIs" alias."""
        if ("APIs REST" in requirements or "APIs de IA" in requirements) and "APIs" in requirements:
            del requirements["APIs"]

    def _remove_redundant_compound_bases(self, requirements: dict[str, Keyword], full_text: str) -> None:
        for compound, base, standalone_base_pattern in _COMPOUND_TERM_PAIRS:
            if compound in requirements and base in requirements and not re.search(standalone_base_pattern, full_text):
                del requirements[base]

    def extract_job_requirements(
        self, job_estruturada: dict[str, str | list[str]],
    ) -> list[Keyword]:
        """Extract known catalog entries only from score-relevant areas."""

        requirements: dict[str, Keyword] = {}
        offset = self._add_matches_from_weighted_sections(job_estruturada, requirements)
        self._add_matches_from_title(job_estruturada, requirements)
        full_text = self._add_context_matches(job_estruturada, requirements, offset)
        self._remove_redundant_generic_apis(requirements)
        self._remove_redundant_compound_bases(requirements, full_text)

        return sorted(requirements.values(), key=lambda item: (-item.weight, item.priority))

    def extract_weighted_relevant_keywords(self, text_job: str, limite: int = 40) -> list[Keyword]:
        return self.extract_job_requirements(normalize_job_text(text_job))[:limite]

    def extract_relevant_keywords(self, text_job: str, limite: int = 40) -> list[str]:
        return [item.term for item in self.extract_weighted_relevant_keywords(text_job, limite)]

    def detect_missing_sections(self, resume_text: str) -> list[str]:
        sections = extract_resume_sections(resume_text)

        return [
            f"Seção de {name} não identificada no currículo."
            for name, key in EXPECTED_SECTIONS.items()
            if key not in sections
        ]

    def _contains_direct(self, text: str, name: str) -> bool:
        cleaned = text
        for compound in _COMPOUND_TERM_STRIP_MAP.get(name, ()):
            cleaned = re.sub(re.escape(compound), " ", cleaned, flags=re.I)
        return self._contains(cleaned, name)

    def _locate_in_primary_sections(
        self, sections: dict[str, str], name: str
    ) -> tuple[EvidenceLevel, str, None] | None:
        if self._contains_direct(sections.get("professional_experience", ""), name):
            return EvidenceLevel.STRONG_PRACTICAL, "experiência profissional", None

        freelance = sections.get("freelance", "")
        if self._contains_direct(freelance, name):
            delivery = re.search(
                r"\b(entreg|cliente|contrat|publicad|deploy|implement|desenvolv|delivered|client|contract|released|built)\w*\b",
                normalize_for_comparison(freelance),
            )
            return (EvidenceLevel.STRONG_PRACTICAL if delivery else EvidenceLevel.RELATED), "freela", None

        project = sections.get("projects", "")
        if self._contains_direct(project, name):
            return EvidenceLevel.STRONG_PRACTICAL, "project", None

        open_source = sections.get("open_source", "")
        if self._contains_direct(open_source, name):
            contribution = re.search(
                r"\b(contribu|commit|pull request|merged|aceit|corrig|implement|maintain|fixed)\w*\b",
                normalize_for_comparison(open_source),
            )
            return (EvidenceLevel.STRONG_PRACTICAL if contribution else EvidenceLevel.RELATED), "open source", None

        return None

    def _locate_in_partial_or_educational_sections(
        self, sections: dict[str, str], name: str
    ) -> tuple[EvidenceLevel, str, None] | None:
        if any(self._contains_direct(sections.get(s, ""), name) for s in _PARTIAL_PRACTICAL_SECTIONS):
            source = (
                "residência/laboratório prático"
                if self._contains_direct(sections.get("residencies", ""), name)
                else "project acadêmico"
            )
            return EvidenceLevel.PARTIAL_PRACTICAL, source, None

        if any(self._contains_direct(sections.get(s, ""), name) for s in _EDUCATIONAL_SECTIONS):
            return EvidenceLevel.EDUCATIONAL, "curso/formação", None

        return None

    def _locate_by_line_scan(self, resume: str, name: str) -> tuple[EvidenceLevel, str, None] | None:
        for line in resume.splitlines():
            normalized_line = normalize_for_comparison(line)
            if not self._contains_direct(line, name):
                continue
            if re.search(r"\b(curso|certifica|disciplina|formacao|bootcamp|treinamento)\b", normalized_line):
                return EvidenceLevel.EDUCATIONAL, "curso/formação", None
            if re.search(r"\b(residencia tecnologica|laboratorio pratico|lab pratico)\b", normalized_line):
                return EvidenceLevel.PARTIAL_PRACTICAL, "residência/laboratório prático", None
        return None

    def _locate_by_inference(self, resume: str, name: str) -> tuple[EvidenceLevel, str, str] | None:
        corpus = normalize_for_comparison(resume)
        for inference in inferences_for(name):
            try:
                origin_present = self._contains(resume, inference.origin)
            except StopIteration:
                origin_present = normalize_for_comparison(inference.origin) in corpus
            context_ok = not inference.requires_context or any(
                term in corpus for term in inference.requires_context
            )
            if origin_present and context_ok:
                return EvidenceLevel.RELATED, inference.origin, inference.strength.value
        return None

    def _locate_evidence(
        self, resume: str, sections: dict[str, str], name: str
    ) -> tuple[EvidenceLevel, str | None, str | None]:
        return (
            self._locate_in_primary_sections(sections, name)
            or self._locate_in_partial_or_educational_sections(sections, name)
            or self._locate_by_line_scan(resume, name)
            or self._locate_standalone_skill(resume, sections, name)
            or self._locate_by_inference(resume, name)
            or (EvidenceLevel.ABSENT, None, None)
        )

    def _locate_standalone_skill(
        self, resume: str, sections: dict[str, str], name: str
    ) -> tuple[EvidenceLevel, str, None] | None:
        if self._contains_direct(sections.get("technical_skills", ""), name) or self._contains_direct(resume, name):
            return EvidenceLevel.STANDALONE_SKILL, "competências", None
        return None

    def _evidence_text(self, term: str, source: str | None, evidence_level: EvidenceLevel) -> str | None:
        if not source:
            return None
        if evidence_level != EvidenceLevel.RELATED:
            return f"{term} aparece em {source}."
        return f"{source} fornece evidência técnica relacionada, sem comprovar {term} diretamente."

    def _guidance_for(self, evidence_level: EvidenceLevel, source: str | None, term: str) -> str:
        if evidence_level in {EvidenceLevel.STRONG_PRACTICAL, EvidenceLevel.PARTIAL_PRACTICAL}:
            return "Mantenha a evidência objetiva e descreva uso, entrega e resultado alcançado."
        if evidence_level == EvidenceLevel.EDUCATIONAL:
            return "Mantenha como formação/conhecimento; associe a project real somente se essa aplicação existiu."
        if evidence_level == EvidenceLevel.STANDALONE_SKILL:
            return "Associe a habilidade a project ou experiência real, se possível."
        if evidence_level == EvidenceLevel.RELATED:
            return f"A relação com {source} é indício, não comprovação direta; explicite somente se tiver vivência real."
        return f"Não inclua {term} como experiência se não tiver usado. Pode criar project prático para evidenciar."

    def _build_requirement_item(
        self, requirement: Keyword, resume: str, sections: dict[str, str]
    ) -> RequirementAnalysisItem:
        evidence_level, source, strength = self._locate_evidence(resume, sections, requirement.term)
        return RequirementAnalysisItem(
            item=requirement.term,
            type="technology" if requirement.technology else "requirement",
            category=requirement.grupo,
            weight=requirement.weight,
            status=public_status(evidence_level),
            resume_evidence=self._evidence_text(requirement.term, source, evidence_level),
            guidance=self._guidance_for(evidence_level, source, requirement.term),
            evidence_level=evidence_level.value,
            evidence_source=source,
            inference_strength=strength,
        )

    def compare_resume_to_job(
        self, resume: str, sections: dict[str, str], requirements: list[Keyword]
    ) -> list[RequirementAnalysisItem]:
        """Classify each requirement without copying personal data."""
        return [self._build_requirement_item(requirement, resume, sections) for requirement in requirements]


def extract_job_requirements(job_estruturada: dict[str, str | list[str]]) -> list[Keyword]:
    return RequirementExtractor().extract_job_requirements(job_estruturada)


def extract_weighted_relevant_keywords(text_job: str, limite: int = 40) -> list[Keyword]:
    return RequirementExtractor().extract_weighted_relevant_keywords(text_job, limite)


def extract_relevant_keywords(text_job: str, limite: int = 40) -> list[str]:
    return RequirementExtractor().extract_relevant_keywords(text_job, limite)


def detect_missing_sections(resume_text: str) -> list[str]:
    return RequirementExtractor().detect_missing_sections(resume_text)


def compare_resume_to_job(
    resume: str, sections: dict[str, str], requirements: list[Keyword]
) -> list[RequirementAnalysisItem]:
    return RequirementExtractor().compare_resume_to_job(resume, sections, requirements)
