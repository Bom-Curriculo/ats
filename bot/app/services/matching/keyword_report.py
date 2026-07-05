import re

from app.models.analysis import RequirementAnalysisItem, ItemKeyword, KeywordReport
from app.services.matching.common_terms import SQL_TERMS
from app.services.matching.interfaces import KeywordReportBuilderInterface
from app.services.normalization.text_normalizer import normalize_for_comparison

WEIGHTS = {"hard_skills": 2.0, "title_function_keywords": 1.5, "business_context": 1.0,
         "action_keywords": 1.0, "domain_keywords": 1.0}

HARD_FILTER_PATTERNS = (
    r"\b\d+\+?\s*anos?\b",
    r"graduacao completa",
    r"ingles avancado",
    r"\b(?:presencial|hibrid[oa])\b",
)


def _hard_filters(job: str, resume: str) -> tuple[list[ItemKeyword], list[str]]:
    filters: list[ItemKeyword] = []
    alerts: list[str] = []
    job_n, resume_n = normalize_for_comparison(job), normalize_for_comparison(resume)

    for pattern in HARD_FILTER_PATTERNS:
        for match in re.finditer(pattern, job_n):
            term = match.group(0)
            present = term in resume_n

            filters.append(ItemKeyword(term=term, category="hard_filters", weight=0, present=present))
            if not present:
                alerts.append(f"Possível impeditivo: hard filter não comprovado no currículo: {term}.")

    return filters, list(dict.fromkeys(alerts))


class KeywordReportBuilder(KeywordReportBuilderInterface):
    """Group requirement items into weighted keyword categories and score coverage."""

    def _category_for(self, item: RequirementAnalysisItem, title_normalized: str) -> str:
        if item.type == "technology":
            return "hard_skills"
        if title_normalized and normalize_for_comparison(item.item) in title_normalized:
            return "title_function_keywords"
        if item.category == "responsabilidade":
            return "action_keywords"
        if item.category == "context":
            return "business_context"
        return "domain_keywords"

    def _group_by_category(
        self, items: list[RequirementAnalysisItem], title: str
    ) -> dict[str, list[ItemKeyword]]:
        title_normalized = normalize_for_comparison(title)
        groups: dict[str, list[ItemKeyword]] = {k: [] for k in WEIGHTS}

        for item in items:
            category = self._category_for(item, title_normalized)
            present = item.status in {"found_with_evidence", "found_without_clear_context"}
            groups[category].append(
                ItemKeyword(term=item.item, category=category, weight=WEIGHTS[category], present=present, source=item.evidence_source)
            )

        return groups

    def _coverage_score(self, keywords: list[ItemKeyword]) -> int:
        """SQL commands are collapsed into one weight so they don't dominate the score."""
        sql = [kw for kw in keywords if kw.term in SQL_TERMS]
        scoreable = [kw for kw in keywords if kw.term not in SQL_TERMS]

        total = sum(kw.weight for kw in scoreable)
        achieved = sum(kw.weight for kw in scoreable if kw.present)
        if sql:
            sql_weight = max(kw.weight for kw in sql)
            total += sql_weight
            if any(kw.present for kw in sql):
                achieved += sql_weight

        return round(achieved / total * 100) if total else 0

    def build(
        self, items: list[RequirementAnalysisItem], job: str, resume: str, title: str = ""
    ) -> tuple[KeywordReport, int, list[ItemKeyword], list[ItemKeyword]]:
        groups = self._group_by_category(items, title)
        filters, alerts = _hard_filters(job, resume)
        all_keywords = [kw for values in groups.values() for kw in values]

        score = self._coverage_score(all_keywords)
        report = KeywordReport(**groups, hard_filters=filters, hard_filter_alerts=alerts)
        return report, score, [x for x in all_keywords if x.present], [x for x in all_keywords if not x.present]


def build_keyword_report(
    items: list[RequirementAnalysisItem], job: str, resume: str, title: str = ""
) -> tuple[KeywordReport, int, list[ItemKeyword], list[ItemKeyword]]:
    return KeywordReportBuilder().build(items, job, resume, title)
