import re

from app.services.matching.technology_catalog import TECHNOLOGY_CATALOG
from app.services.normalization.text_normalizer import normalize_for_comparison, normalize_resume_text
from app.services.matching.technical_matching import contains_alias
from app.services.parsing.interfaces import ResumeInventoryBuilderInterface

_INVENTORY_CATEGORIES = (
    "linguagens", "frontend", "backend", "mobile", "bancos_data",
    "devops", "cloud", "testes", "ferramentas", "metodologias",
    "processos", "ia", "automacao", "arquitetura", "produto",
    "design", "outros", "languages", "education", "projetos_detectados",
)


class ResumeInventoryBuilder(ResumeInventoryBuilderInterface):
    """Detect which technology/skill categories are present in a resume."""

    def build(self, text: str, sections: dict[str, str] | None = None) -> dict[str, list[str]]:
        normalized = normalize_for_comparison(normalize_resume_text(text))

        categories: dict[str, list[str]] = {name: [] for name in _INVENTORY_CATEGORIES}

        for technology in TECHNOLOGY_CATALOG:
            if contains_alias(normalized, technology.aliases):
                categories.setdefault(technology.category, []).append(technology.name)

        if "ingles" in normalized:
            categories["languages"].append("Inglês")

        if re.search(r"graduacao|formacao|bacharel|tecnologo", normalized):
            categories["education"].append("Formação acadêmica detectada")
        if sections and sections.get("projects"):
            categories["projetos_detectados"].append("Seção de projects detectada")

        categories["habilidades_detectadas"] = [
            item for name, items in categories.items()
            if name not in {"education", "projetos_detectados"}
            for item in items
        ]

        categories["habilidades_nao_exigidas_pela_job"] = []
        return categories


def extract_resume_inventory(text: str, sections: dict[str, str] | None = None) -> dict[str, list[str]]:
    return ResumeInventoryBuilder().build(text, sections)
