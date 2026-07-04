"""Bounded local retrieval of job-relevant evidence."""

from app.schemas.analysis import FactBank, KeywordReport
from app.schemas.ai_pipeline import SelectedEvidence
from app.services.text_normalizer import normalize_for_comparison
from app.services.privacy_sanitizer import sanitize_personal_data


SOURCE_STRENGTH = {"experiência profissional": 5, "project": 4, "residência/laboratório prático": 3,
               "curso/formação": 2, "competências": 1, "languages": 1}


def select_relevant_evidence_for_job(
    fact_bank: FactBank | None, requirements: list, keyword_report: KeywordReport | None,
    seniority: str = "not_provided", limite: int = 20,
) -> list[SelectedEvidence]:
    if not fact_bank:
        return []

    names = [getattr(r, "item", str(r)) for r in requirements]

    hard_filters = [x.term for x in keyword_report.hard_filters] if keyword_report else []
    alvos = {normalize_for_comparison(x): x for x in names + hard_filters}


    candidates: list[tuple[int, SelectedEvidence]] = []
    for evidence in fact_bank.evidence_items:
        item = str(evidence.get("item", ""))
        source = evidence.get("source")


        relacionados = [original for key, original in alvos.items() if key in normalize_for_comparison(item) or normalize_for_comparison(item) in key]
        if not relacionados:
            continue
        excerpt = sanitize_personal_data(str(evidence.get("evidence", ""))).text_sanitized[:500]
        level = {"experiência profissional": "pratica_forte", "project": "pratica_projeto",
                 "curso/formação": "educacional", "competências": "skill_solta"}.get(source, "relacionada")
        bonus = 2 if seniority in {"pleno", "senior"} and source == "experiência profissional" else 0
        score = SOURCE_STRENGTH.get(source, 0) + bonus + len(relacionados)


        candidates.append((score, SelectedEvidence(item=item, source=source, source_type=source,
            excerpt=excerpt, evidence_level=level, confidence=min(95, 55 + score * 5), related_to=relacionados)))
    candidates.sort(key=lambda x: (-x[0], x[1].item.casefold()))

    output, vistos = [], set()

    for _, evidence in candidates:

        # Technical note removed during English standardization.
        key = evidence.item.casefold()

        if key not in vistos:
            vistos.add(key)
            output.append(evidence)

        if len(output) >= min(limite, 20):
            break
    return output
