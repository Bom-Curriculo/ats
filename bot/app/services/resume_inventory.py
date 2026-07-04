import re

from app.services.technology_catalog import TECHNOLOGY_CATALOG
from app.services.text_normalizer import normalize_for_comparison, normalize_resume_text
from app.services.technical_matching import contains_alias


# Implementation note.
def _presente(text: str, aliases: tuple[str, ...]) -> bool:
    return contains_alias(text, aliases)


def extract_resume_inventory(text: str, sections: dict[str, str] | None = None) -> dict[str, list[str]]:
    normalized = normalize_for_comparison(normalize_resume_text(text))

    # Implementation note.
    categories = {name: [] for name in (
        "linguagens", "frontend", "backend", "mobile", "bancos_data",
        "devops", "cloud", "testes", "ferramentas", "metodologias",
        "processos", "ia", "automacao", "arquitetura", "produto",
        "design", "outros", "languages", "education", "projetos_detectados",
    )}


    # Implementation note.
    for technology in TECHNOLOGY_CATALOG:
        if _presente(normalized, technology.aliases):
            categories.setdefault(technology.category, []).append(technology.name)


    # Implementation note.
    if "ingles" in normalized:
        categories["languages"].append("Inglês")


    # Implementation note.
    if re.search(r"graduacao|formacao|bacharel|tecnologo", normalized):
        categories["education"].append("Formação acadêmica detectada")
    # Technical note removed during English standardization.
    #
    if sections and sections.get("projects"):
        categories["projetos_detectados"].append("Seção de projects detectada")


    # junta td em habilidades_detectadas (menos formacao e projects)
    categories["habilidades_detectadas"] = [
        item for name, items in categories.items()
        if name not in {"education", "projetos_detectados"}
        for item in items

    ]

    # Implementation note.
    categories["habilidades_nao_exigidas_pela_job"] = []
    return categories
