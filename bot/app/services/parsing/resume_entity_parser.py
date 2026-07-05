"""Parse entities from sections that were already classified."""

import re

from app.services.matching.technology_catalog import TECHNOLOGY_CATALOG
from app.services.matching.technical_matching import contains_alias
from app.services.parsing.interfaces import ResumeEntityParserInterface

STACK_PREFIXES = re.compile(r"(?i)^\s*(?:tecnologias?|technology|technologies|stack|tech stack)\s*:\s*(.+)$")
BULLET = re.compile(r"^\s*[-•*]\s*")


def technologies_in_text(text: str) -> list[str]:
    return [t.name for t in TECHNOLOGY_CATALOG if contains_alias(text, t.aliases, t.name)]


class ResumeEntityParser(ResumeEntityParserInterface):
    """Parse projects and generic evidence blocks from classified resume sections."""

    def _looks_like_title(self, line: str, next_line: str = "") -> bool:
        cleaned = BULLET.sub("", line).strip()
        if not cleaned or STACK_PREFIXES.match(cleaned) or len(cleaned) > 90 or len(cleaned.split()) > 12:
            return False

        if re.search(r"[.!?]$", cleaned) or re.match(r"(?i)^(desenvolv|implement|criad|respons|utiliz|built|developed|implemented)\b", cleaned):
            return False
        return bool(STACK_PREFIXES.match(next_line) or " | " in cleaned or re.match(r"(?i)^(project|project)\s+", cleaned))

    def extract_projects(self, text: str, *, source_type: str = "project") -> list[dict]:
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if not lines:
            return []

        starts = [i for i, line in enumerate(lines)
                   if self._looks_like_title(line, lines[i + 1] if i + 1 < len(lines) else "")]
        if not starts:
            return [{"name": None, "technologies": technologies_in_text(text), "descricao": text[:2000],
                     "evidence_items_entrega": [x for x in lines if BULLET.match(x)][:12],
                     "source": source_type, "confidence": 45, "low_confidence": True,
                     "reason": "Seção de projects sem delimitadores claros."}]

        projects = []
        for pos, start in enumerate(starts):
            end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
            block = lines[start:end]
            name = BULLET.sub("", block[0]).strip()
            declared_stack = [STACK_PREFIXES.match(x).group(1) for x in block[1:] if STACK_PREFIXES.match(x)]
            description_lines = [x for x in block[1:] if not STACK_PREFIXES.match(x)]

            description = "\n".join(description_lines)
            deliveries = [BULLET.sub("", x).strip() for x in description_lines
                        if BULLET.match(x) or re.search(r"(?i)\b(entreg|publicad|deploy|implement|desenvolv|automat|integ|built|released|delivered|implemented)\w*\b", x)]
            corpus = " ".join(block + declared_stack)

            projects.append({"name": name, "technologies": technologies_in_text(corpus),
                             "descricao": description[:2000], "evidence_items_entrega": deliveries[:12],
                             "source": source_type, "confidence": 90 if declared_stack else 75,
                             "low_confidence": False, "reason": None})

        return projects

    def section_block(self, text: str, source: str, confidence: int = 90) -> list[dict]:
        if not text.strip():
            return []

        return [{"content": text.strip()[:5000], "source": source, "confidence": confidence,
                 "low_confidence": confidence < 60, "reason": None if confidence >= 60 else "Fonte inferida sem heading confiável."}]


def extract_projects(text: str, *, source_type: str = "project") -> list[dict]:
    return ResumeEntityParser().extract_projects(text, source_type=source_type)


def section_block(text: str, source: str, confidence: int = 90) -> list[dict]:
    return ResumeEntityParser().section_block(text, source, confidence)
