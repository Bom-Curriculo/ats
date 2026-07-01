import re

from app.services.normalizador_texto import normalizar_para_comparacao


def padrao_alias(alias: str) -> re.Pattern[str]:
    termo = normalizar_para_comparacao(alias)

    # Limites alfanuméricos evitam Java/JavaScript, RAG/drag e IA/parciais.
    return re.compile(rf"(?<![\w]){re.escape(termo)}(?![\w])", re.IGNORECASE)


def encontrar_alias(texto: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    corpus = normalizar_para_comparacao(texto)
    encontrados = [m for alias in aliases for m in padrao_alias(alias).finditer(corpus)]
    return min(encontrados, key=lambda m: m.start()) if encontrados else None


def contem_alias(texto: str, aliases: tuple[str, ...], nome: str | None = None) -> bool:
    corpus = normalizar_para_comparacao(texto)
    for alias in aliases:
        for match in padrao_alias(alias).finditer(corpus):
            janela = corpus[max(0, match.start() - 12):match.end() + 18]

            # somente aliases explícitos representam API
            if nome == "APIs" and re.search(r"apis?\s+(?:de\s+)?ia|ai\s+apis?", janela):
                continue
            return True
    return False
