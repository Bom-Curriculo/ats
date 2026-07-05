import re

from app.services.matching.common_terms import BRAZILIAN_CITIES
from app.services.normalization.interfaces import JobNormalizerInterface
from app.services.normalization.text_normalizer import (
    normalize_for_comparison,
    normalize_resume_text,
)

# Common boilerplate found in job-board descriptions.
DISCARDED_LINES = (
    r"\bapply(?:\s+on)?\b",
    r"\bvia\b",
    r"\bindeed\b",
    r"\bglassdoor\b",
    r"\blinkedin\b",
    r"\bgupy\b",
    r"\bsolides\b",
    r"\bquickin\b",
    r"\bbebee\b",
    r"\bjob\s+description\b",
    r"\b\d+\s+days?\s+ago\b",
    r"\bfull[ -]?time\b",
    r"\bstate\s+of\b",
    r"\bc[oó]digo\s+da\s+vaga\b",
)

BENEFITS_HEADER = re.compile(
    r"(?i)^\s*(benef[ií]cios|o que oferecemos|vantagens|perks)\s*:?\s*$"
)

RELEVANT_HEADER = re.compile(
    r"(?i)^\s*(requisitos|requirements|qualifica[cç][oõ]es|qualifications|responsabilidades|responsibilities|atividades|"
    r"diferenciais|differentials|preferred|nice to have|tecnologias|technologies|stack|sobre a vaga|about the role)\b"
)

# (key prefixes, target group, does the header line also carry inline content)
_SECTION_HEADER_RULES = (
    (("responsibilities", "atividades", "responsibilities"), "responsibilities", True),
    (("requisitos", "requirements", "qualificacoes", "qualifications", "technologies", "technologies", "stack"), "requirements_obrigatorios", True),
    (("diferenciais", "differentials", "desejaveis", "desejveis", "preferred", "nice to have"), "differentials", True),
    (("benefcios", "beneficios", "o que oferecemos", "vantagens", "perks"), "beneficios", False),
    (("sobre a empresa", "quem somos", "nossa empresa"), "informacoes_institucionais", False),
)

_SINGLE_WORD_REQUIREMENT_KEYS = {
    "front end", "frontend", "back end", "backend", "banco de dados", "devops", "versionamento",
}

_AREA_SIGNALS = (
    ("full stack", ("full stack", "fullstack")),
    ("front-end", ("front-end", "frontend")),
    ("back-end", ("back-end", "backend")),
    ("data", ("data", "data engineer", "data analyst")),
    ("mobile", ("mobile", "android", "ios")),
    ("devops", ("devops", "sre")),
    ("qa", ("qa", "quality assurance", "testes")),
    ("suporte", ("suporte", "support")),
    ("automação", ("automacao", "automation")),
    ("ia", ("inteligencia artificial", "machine learning", "llm", " rag ")),
)


class JobNormalizer(JobNormalizerInterface):
    """Structure job-post content and strip boilerplate without letting benefits affect scoring."""

    def _strip_noise(self, line: str) -> str:
        cleaned = line
        for pattern in DISCARDED_LINES:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip(" -|•")

    def clean_job_text(self, text: str) -> str:
        text = normalize_resume_text(text)
        cleaned_lines: list[str] = []
        skipping_benefits = False

        for line in text.splitlines():
            if BENEFITS_HEADER.match(line):
                skipping_benefits = True
                continue

            if skipping_benefits and RELEVANT_HEADER.match(line):
                skipping_benefits = False

            if skipping_benefits:
                continue

            cleaned = self._strip_noise(line)
            if cleaned:
                cleaned_lines.append(cleaned)

        return "\n".join(cleaned_lines)

    def _inline_content(self, value: str) -> str:
        """Text after a "Header: ..." or "Header ..." prefix on the same line."""
        if ":" in value:
            return value.partition(":")[2].strip()
        parts = value.split(maxsplit=1)
        return parts[1].strip() if len(parts) == 2 else ""

    def _classify_line(self, key: str, line: str) -> tuple[str | None, str | None]:
        """Return (new_group, content). Either half may be `None`.

        `new_group` is `None` when the line doesn't start a new section (the
        current group carries over). `content` is `None` when the line itself
        has nothing to append (a bare section header, or inline content that
        stripped down to nothing).
        """
        if key in _SINGLE_WORD_REQUIREMENT_KEYS:
            return "requirements_obrigatorios", None

        for prefixes, group, has_inline_content in _SECTION_HEADER_RULES:
            if key.startswith(prefixes):
                if has_inline_content:
                    return group, (self._inline_content(line) or None)
                return group, None

        return None, line

    def _extract_modality(self, comparison: str) -> str:
        match = re.search(r"(?i)\b(remoto|h[ií]brid[oa]|presencial)\b", comparison)
        return match.group(1) if match else ""

    def _extract_location(self, comparison: str) -> str:
        return next((c for c in BRAZILIAN_CITIES if c.lower() in comparison.lower()), "")

    def _extract_company(self, text: str) -> str:
        match = re.search(r"(?im)^\s*(?:empresa|company)\s*:\s*([^\n]+)", text)
        return match.group(1).strip() if match else ""

    def _extract_area(self, corpus: str) -> str:
        return next((area for area, signals in _AREA_SIGNALS if any(s in corpus for s in signals)), "")

    def _accepts_no_experience(self, corpus: str) -> bool:
        return bool(re.search(
            r"(?i)\b(?:sem experiencia|nao exige experiencia|no experience|required experience: none|experience not required)\b",
            corpus,
        ))

    def normalize_job_text(self, text: str) -> dict[str, str | list[str]]:
        """Structure job content without allowing benefits to affect scoring."""

        fields: dict[str, str | list[str]] = {
            "title": "",
            "company": "",
            "area": "",
            "localidade": "",
            "modality": "",
            "responsibilities": [],
            "requirements_obrigatorios": [],
            "differentials": [],
            "beneficios": [],
            "informacoes_institucionais": [],
        }

        group = "informacoes_institucionais"

        for original_line in normalize_resume_text(text).splitlines():
            line = self._strip_noise(original_line)
            if not line:
                continue

            key = re.sub(r"[^a-z ]", "", normalize_for_comparison(line)).strip()
            new_group, content = self._classify_line(key, line)
            if new_group:
                group = new_group
            if content is None:
                continue

            if not fields["title"] and group == "informacoes_institucionais":
                fields["title"] = content
            else:
                assert isinstance(fields[group], list)
                fields[group].append(content)

        comparison = normalize_resume_text(text)
        corpus = normalize_for_comparison(text)
        fields["modality"] = self._extract_modality(comparison)
        fields["localidade"] = self._extract_location(comparison)
        fields["company"] = self._extract_company(text)
        fields["area"] = self._extract_area(corpus)
        fields["accepts_no_experience"] = self._accepts_no_experience(corpus)

        return fields


def clean_job_text(text: str) -> str:
    return JobNormalizer().clean_job_text(text)


def normalize_job_text(text: str) -> dict[str, str | list[str]]:
    return JobNormalizer().normalize_job_text(text)
