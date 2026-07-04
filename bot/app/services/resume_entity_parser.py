"""Parse entities from sections that were already classified."""

import re

from app.services.technology_catalog import TECHNOLOGY_CATALOG
from app.services.technical_matching import contains_alias


STACK_PREFIXES = re.compile(r"(?i)^\s*(?:tecnologias?|technology|technologies|stack|tech stack)\s*:\s*(.+)$")
BULLET = re.compile(r"^\s*[-•*]\s*")


def technologies_in_text(text: str) -> list[str]:
    return [t.name for t in TECHNOLOGY_CATALOG if contains_alias(text, t.aliases, t.name)]


def _looks_like_title(line: str, proxima: str = "") -> bool:
    limpa = BULLET.sub("", line).strip()
    if not limpa or STACK_PREFIXES.match(limpa) or len(limpa) > 90 or len(limpa.split()) > 12:
        return False

    if re.search(r"[.!?]$", limpa) or re.match(r"(?i)^(desenvolv|implement|criad|respons|utiliz|built|developed|implemented)\b", limpa):
        return False
    return bool(STACK_PREFIXES.match(proxima) or " | " in limpa or re.match(r"(?i)^(project|project)\s+", limpa))


def extract_projects(text: str, *, source_type: str = "project") -> list[dict]:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if not lines:
        return []

    inicios = [i for i, line in enumerate(lines)
               if _looks_like_title(line, lines[i + 1] if i + 1 < len(lines) else "")]
    if not inicios:
        return [{"name": None, "technologies": technologies_in_text(text), "descricao": text[:2000],
                 "evidence_items_entrega": [x for x in lines if BULLET.match(x)][:12],
                 "source": source_type, "confidence": 45, "low_confidence": True,
                 "reason": "Seção de projects sem delimitadores claros."}]


    projects = []
    for pos, inicio in enumerate(inicios):


        fim = inicios[pos + 1] if pos + 1 < len(inicios) else len(lines)
        bloco = lines[inicio:fim]
        name = BULLET.sub("", bloco[0]).strip()
        stack_explica = [STACK_PREFIXES.match(x).group(1) for x in bloco[1:] if STACK_PREFIXES.match(x)]
        descricao_linhas = [x for x in bloco[1:] if not STACK_PREFIXES.match(x)]

        descricao = "\n".join(descricao_linhas)
        entregas = [BULLET.sub("", x).strip() for x in descricao_linhas
                    if BULLET.match(x) or re.search(r"(?i)\b(entreg|publicad|deploy|implement|desenvolv|automat|integ|built|released|delivered|implemented)\w*\b", x)]
        corpus = " ".join(bloco + stack_explica)

        projects.append({"name": name, "technologies": technologies_in_text(corpus),
                         "descricao": descricao[:2000], "evidence_items_entrega": entregas[:12],
                         "source": source_type, "confidence": 90 if stack_explica else 75,
                         "low_confidence": False, "reason": None})


    return projects


def section_block(text: str, source: str, confidence: int = 90) -> list[dict]:
    if not text.strip():
        return []

    return [{"content": text.strip()[:5000], "source": source, "confidence": confidence,
             "low_confidence": confidence < 60, "reason": None if confidence >= 60 else "Fonte inferida sem heading confiável."}]
