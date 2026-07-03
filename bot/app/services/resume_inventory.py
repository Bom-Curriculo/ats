import re

from app.services.technology_catalog import CATALOGO
from app.services.text_normalizer import normalize_for_comparison, normalize_resume_text
from app.services.technical_matching import contains_alias


# wrapper so pra manter compatibilidade
def _presente(texto: str, aliases: tuple[str, ...]) -> bool:
    return contains_alias(texto, aliases)


def extract_resume_inventory(texto: str, secoes: dict[str, str] | None = None) -> dict[str, list[str]]:
    normalizado = normalize_for_comparison(normalize_resume_text(texto))

    # cria dict com td que pode ser classificado
    categorias = {nome: [] for nome in (
        "linguagens", "frontend", "backend", "mobile", "bancos_dados",
        "devops", "cloud", "testes", "ferramentas", "metodologias",
        "processos", "ia", "automacao", "arquitetura", "produto",
        "design", "outros", "idiomas", "formacao", "projetos_detectados",
    )}


    # varre o catálogo e joga na categoria certa
    for tecnologia in CATALOGO:
        if _presente(normalizado, tecnologia.aliases):
            categorias.setdefault(tecnologia.categoria, []).append(tecnologia.nome)


    # inglês genérioco detectado
    if "ingles" in normalizado:
        categorias["idiomas"].append("Inglês")


    # formacao genérica detectada
    if re.search(r"graduacao|formacao|bacharel|tecnologo", normalizado):
        categorias["formacao"].append("Formação acadêmica detectada")
    # seção de projetos encontrada
    #
    if secoes and secoes.get("projetos"):
        categorias["projetos_detectados"].append("Seção de projetos detectada")


    # junta td em habilidades_detectadas (menos formacao e projetos)
    categorias["habilidades_detectadas"] = [
        item for nome, itens in categorias.items()
        if nome not in {"formacao", "projetos_detectados"}
        for item in itens

    ]

    # placeholder preenchido depois no pipeline principal
    categorias["habilidades_nao_exigidas_pela_vaga"] = []
    return categorias
