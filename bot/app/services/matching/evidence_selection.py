"""Bounded local retrieval of job-relevant evidence."""

from app.models.analysis import FactBank, KeywordReport
from app.models.ai_pipeline import SelectedEvidence
from app.services.matching.interfaces import EvidenceSelectorInterface
from app.services.normalization.text_normalizer import normalize_for_comparison
from app.services.privacy.interfaces import SanitizerInterface
from app.services.privacy.sanitizer import PrivacySanitizer

SOURCE_STRENGTH = {"experiência profissional": 5, "project": 4, "residência/laboratório prático": 3,
               "curso/formação": 2, "competências": 1, "languages": 1}


class EvidenceSelector(EvidenceSelectorInterface):
    """Select and rank the fact-bank evidence most relevant to a job's requirements."""

    def select(
        self, fact_bank: FactBank | None, requirements: list, keyword_report: KeywordReport | None,
        seniority: str = "not_provided", limit: int = 20, sanitizer: SanitizerInterface | None = None,
    ) -> list[SelectedEvidence]:
        if not fact_bank:
            return []

        sanitizer = sanitizer or PrivacySanitizer()
        names = [getattr(r, "item", str(r)) for r in requirements]

        hard_filters = [x.term for x in keyword_report.hard_filters] if keyword_report else []
        targets = {normalize_for_comparison(x): x for x in names + hard_filters}

        candidates: list[tuple[int, SelectedEvidence]] = []
        for evidence in fact_bank.evidence_items:
            item = str(evidence.get("item", ""))
            source = evidence.get("source")

            related = [original for key, original in targets.items() if key in normalize_for_comparison(item) or normalize_for_comparison(item) in key]
            if not related:
                continue
            excerpt = sanitizer.sanitize(str(evidence.get("evidence", ""))).text_sanitized[:500]
            level = {"experiência profissional": "pratica_forte", "project": "pratica_projeto",
                     "curso/formação": "educacional", "competências": "skill_solta"}.get(source, "relacionada")
            bonus = 2 if seniority in {"pleno", "senior"} and source == "experiência profissional" else 0
            score = SOURCE_STRENGTH.get(source, 0) + bonus + len(related)

            candidates.append((score, SelectedEvidence(item=item, source=source, source_type=source,
                excerpt=excerpt, evidence_level=level, confidence=min(95, 55 + score * 5), related_to=related)))
        candidates.sort(key=lambda x: (-x[0], x[1].item.casefold()))

        output, seen = [], set()

        for _, evidence in candidates:
            key = evidence.item.casefold()

            if key not in seen:
                seen.add(key)
                output.append(evidence)

            if len(output) >= min(limit, 20):
                break
        return output


def select_relevant_evidence_for_job(
    fact_bank: FactBank | None, requirements: list, keyword_report: KeywordReport | None,
    seniority: str = "not_provided", limite: int = 20, sanitizer: SanitizerInterface | None = None,
) -> list[SelectedEvidence]:
    return EvidenceSelector().select(fact_bank, requirements, keyword_report, seniority, limite, sanitizer)
