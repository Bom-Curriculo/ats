import re

from app.schemas.analysis import RequirementAnalysisItem, ItemKeyword, KeywordReport
from app.services.text_normalizer import normalize_for_comparison


WEIGHTS = {"hard_skills": 2.0, "title_function_keywords": 1.5, "business_context": 1.0,
         "action_keywords": 1.0, "domain_keywords": 1.0}


def _hard_filters(job: str, resume: str) -> tuple[list[ItemKeyword], list[str]]:
    filtros: list[ItemKeyword] = []

    alerts: list[str] = []
    job_n, cv_n = normalize_for_comparison(job), normalize_for_comparison(resume)
    patterns = [r"\b\d+\+?\s*anos?\b", r"graduacao completa", r"ingles avancado",
               r"\b(?:presencial|hibrid[oa])\b"]

    for pattern in patterns:
        for match in re.finditer(pattern, job_n):
            term = match.group(0)
            present = term in cv_n

            filtros.append(ItemKeyword(term=term, category="hard_filters", weight=0, present=present))
            if not present:
                alerts.append(f"Possível impeditivo: hard filter não comprovado no currículo: {term}.")

    return filtros, list(dict.fromkeys(alerts))


def build_keyword_report(items: list[RequirementAnalysisItem], job: str, resume: str, title: str = "") -> tuple[KeywordReport, int, list[ItemKeyword], list[ItemKeyword]]:
    grupos: dict[str, list[ItemKeyword]] = {k: [] for k in WEIGHTS}
    title_n = normalize_for_comparison(title)


    for item in items:
        if item.type == "technology":
            category = "hard_skills"

        elif normalize_for_comparison(item.item) in title_n and title_n:
            category = "title_function_keywords"

        elif item.category == "responsabilidade":
            category = "action_keywords"

        elif item.category == "context":
            category = "business_context"

        else:
            category = "domain_keywords"
        present = item.status in {"found_with_evidence", "found_without_clear_context"}
        grupos[category].append(ItemKeyword(term=item.item, category=category, weight=WEIGHTS[category], present=present, source=item.evidence_source))
    filtros, alerts = _hard_filters(job, resume)
    todos = [kw for values in grupos.values() for kw in values]


    # Implementation note.
    sql_names = {"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}
    sql = [kw for kw in todos if kw.term in sql_names]
    pontuaveis = [kw for kw in todos if kw.term not in sql_names]
    total = sum(kw.weight for kw in pontuaveis)
    obtido = sum(kw.weight for kw in pontuaveis if kw.present)
    if sql:
        weight_sql = max(kw.weight for kw in sql)
        total += weight_sql
        if any(kw.present for kw in sql):
            obtido += weight_sql
    score = round(obtido / total * 100) if total else 0
    report = KeywordReport(**grupos, hard_filters=filtros, hard_filter_alerts=alerts)
    return report, score, [x for x in todos if x.present], [x for x in todos if not x.present]
