import re

from app.services.text_normalizer import normalize_for_comparison


def alias_pattern(alias: str) -> re.Pattern[str]:
    term = normalize_for_comparison(alias)

    # Implementation note.
    return re.compile(rf"(?<![\w]){re.escape(term)}(?![\w])", re.IGNORECASE)


def find_alias(text: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    corpus = normalize_for_comparison(text)
    found_items = [m for alias in aliases for m in alias_pattern(alias).finditer(corpus)]
    return min(found_items, key=lambda m: m.start()) if found_items else None


def contains_alias(text: str, aliases: tuple[str, ...], name: str | None = None) -> bool:
    corpus = normalize_for_comparison(text)
    for alias in aliases:
        for match in alias_pattern(alias).finditer(corpus):
            janela = corpus[max(0, match.start() - 12):match.end() + 18]

            # Implementation note.
            if name == "APIs" and re.search(r"apis?\s+(?:de\s+)?ia|ai\s+apis?", janela):
                continue
            return True
    return False
