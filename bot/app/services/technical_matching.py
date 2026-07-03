import re

from app.services.text_normalizer import normalize_for_comparison


def alias_pattern(alias: str) -> re.Pattern[str]:
    termo = normalize_for_comparison(alias)

    # Limites alfanuméricos evitam Java/JavaScript, RAG/drag e IA/parciais.
    return re.compile(rf"(?<![\w]){re.escape(termo)}(?![\w])", re.IGNORECASE)


def find_alias(texto: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    corpus = normalize_for_comparison(texto)
    encontrados = [m for alias in aliases for m in alias_pattern(alias).finditer(corpus)]
    return min(encontrados, key=lambda m: m.start()) if encontrados else None


def contains_alias(texto: str, aliases: tuple[str, ...], nome: str | None = None) -> bool:
    corpus = normalize_for_comparison(texto)
    for alias in aliases:
        for match in alias_pattern(alias).finditer(corpus):
            janela = corpus[max(0, match.start() - 12):match.end() + 18]

            # somente aliases explícitos representam API
            if nome == "APIs" and re.search(r"apis?\s+(?:de\s+)?ia|ai\s+apis?", janela):
                continue
            return True
    return False
