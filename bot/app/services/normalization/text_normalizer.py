import re
import unicodedata

from app.services.normalization.interfaces import TextNormalizerInterface

KNOWN_TITLES = (
    "RESUMO",
    "COMPETÊNCIAS",
    "PROJETOS",
    "EDUCAÇÃO",
    "CERTIFICAÇÕES",
    "EXPERIÊNCIA",
    "FORMAÇÃO",
    "HABILIDADES",
    "TECNOLOGIAS",
    "CURSOS",
    "IDIOMAS",
    "CONQUISTAS",
    "PORTFÓLIO",
    "SUMMARY",
    "WORK EXPERIENCE",
    "PROFESSIONAL EXPERIENCE",
    "PROJECTS",
    "EDUCATION",
    "CERTIFICATIONS",
    "TECHNICAL SKILLS",
    "LANGUAGES",
    "AWARDS",
)

_FRAMEWORK_REPLACEMENTS = (
    (r"(?i)\bnext\s*\.?\s*js\b", "Next.js"),
    (r"(?i)\btailwind(?:\s+css)?\b", "Tailwind CSS"),
    (r"(?i)\bshadcn(?:\s*/\s*ui)?\b", "shadcn/ui"),
    (r"(?i)\bradix(?:\s+ui)?\b", "Radix UI"),
)


def normalize_for_comparison(text: str) -> str:
    """Return a lowercase, accent-free comparison form."""
    return "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    ).lower()


class TextNormalizer(TextNormalizerInterface):
    """Normalize noise introduced by PDF extraction and inconsistent formatting."""

    def _fix_spaced_out_titles(self, text: str) -> str:
        for title in KNOWN_TITLES:
            spaced_pattern = r"\s+".join(re.escape(letter) for letter in title)
            text = re.sub(rf"(?<!\w){spaced_pattern}(?!\w)", title, text, flags=re.IGNORECASE)
        return text

    def normalize_resume_text(self, text: str) -> str:
        text = self._fix_spaced_out_titles(text.replace(" ", " "))

        for pattern, canonical_form in _FRAMEWORK_REPLACEMENTS:
            text = re.sub(pattern, canonical_form, text)

        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def normalize_resume_text(text: str) -> str:
    return TextNormalizer().normalize_resume_text(text)
