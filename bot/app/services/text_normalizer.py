import re
import unicodedata

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


def normalize_for_comparison(text: str) -> str:
    """Return a lowercase, accent-free comparison form."""

    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", text)
        if unicodedata.category(caractere) != "Mn"
    ).lower()


# Technical note removed during English standardization.
def _corrigir_titles_espacados(text: str) -> str:

    for title in KNOWN_TITLES:
        letras = r"\s+".join(re.escape(letra) for letra in title)

        text = re.sub(rf"(?<!\w){letras}(?!\w)", title, text, flags=re.IGNORECASE)

    return text


def normalize_resume_text(text: str) -> str:
    """Normalize noise introduced by PDF extraction."""

    # Implementation note.
    text = _corrigir_titles_espacados(text.replace("\u00a0", " "))

    # Normalize library and framework names distorted by PDF extraction.
    substituicoes = (
        (r"(?i)\bnext\s*\.?\s*js\b", "Next.js"),
        (r"(?i)\btailwind(?:\s+css)?\b", "Tailwind CSS"),
        (r"(?i)\bshadcn(?:\s*/\s*ui)?\b", "shadcn/ui"),
        (r"(?i)\bradix(?:\s+ui)?\b", "Radix UI"),
    )

    for pattern, default_form in substituicoes:
        text = re.sub(pattern, default_form, text)

    # Implementation note.
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]

    return "\n".join(line for line in lines if line)
