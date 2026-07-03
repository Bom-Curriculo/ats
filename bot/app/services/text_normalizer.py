import re
import unicodedata

TITULOS_CONHECIDOS = (
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


def normalize_for_comparison(texto: str) -> str:
    """representação sem acento"""

    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    ).lower()


# titulos de seção que o pdf as vezes separa letra por letra
def _corrigir_titulos_espacados(texto: str) -> str:

    for titulo in TITULOS_CONHECIDOS:
        letras = r"\s+".join(re.escape(letra) for letra in titulo)

        texto = re.sub(rf"(?<!\w){letras}(?!\w)", titulo, texto, flags=re.IGNORECASE)

    return texto


def normalize_resume_text(texto: str) -> str:
    """ruido de pdf"""

    # troca nbsp por espaço normal
    texto = _corrigir_titulos_espacados(texto.replace("\u00a0", " "))

    # padroniza nomes de libs/frameworks q vem feio do pdf
    substituicoes = (
        (r"(?i)\bnext\s*\.?\s*js\b", "Next.js"),
        (r"(?i)\btailwind(?:\s+css)?\b", "Tailwind CSS"),
        (r"(?i)\bshadcn(?:\s*/\s*ui)?\b", "shadcn/ui"),
        (r"(?i)\bradix(?:\s+ui)?\b", "Radix UI"),
    )

    for padrao, forma_padrao in substituicoes:
        texto = re.sub(padrao, forma_padrao, texto)

    # tira espaços extras e linhas vazias
    linhas = [re.sub(r"[ \t]+", " ", linha).strip() for linha in texto.splitlines()]

    return "\n".join(linha for linha in linhas if linha)
