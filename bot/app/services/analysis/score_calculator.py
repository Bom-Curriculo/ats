import re

from app.models.analysis import RequirementAnalysisItem, AnalysisResult
from app.models.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.services.analysis.interfaces import ScoreCalculatorInterface
from app.services.matching.technical_equivalences import (
    EvidenceLevel,
    JobLevel,
    source_weight,
    SUBREQUIREMENT_GROUPS,
)
from app.services.normalization.text_normalizer import normalize_for_comparison

# calculate_ats_score: a near-perfect score from very few requirements is
# unreliable, so it gets capped.
FEW_REQUIREMENTS_THRESHOLD = 5
NEAR_PERFECT_SCORE_CAP = 95

# calculate_final_score weighting/caps.
MIN_AI_CONFIDENCE = 70
LOCAL_ONLY_WEIGHT = 0.8
KEYWORD_ONLY_WEIGHT = 0.2
LOW_ADJUSTMENTS_THRESHOLD = 3
AI_WEIGHT_WITH_FEW_ADJUSTMENTS = 0.35
AI_WEIGHT_WITH_MANY_ADJUSTMENTS = 0.2
LOW_CONTEXT_QUALITY_THRESHOLD = 60
AI_WEIGHT_CAP_ON_LOW_CONTEXT = 0.15
FALLBACK_PENALTY_PER_STEP = 0.07
FALLBACK_PENALTY_CAP = 0.2
MIN_AI_WEIGHT = 0.05
KEYWORD_WEIGHT_WHEN_PROVIDED = 0.2
LOW_LOCAL_SCORE_THRESHOLD = 50
HIGH_AI_SCORE_THRESHOLD = 80
LOW_LOCAL_HIGH_AI_SCORE_CAP = 75
NO_EXPERIENCE_SENIOR_SCORE_CAP = 65
HARD_FILTER_SCORE_BASE = 75
HARD_FILTER_PENALTY_PER_MISSING = 10
HARD_FILTER_SCORE_FLOOR = 35


def _ai_requirement_key(name: str) -> str:
    key = normalize_for_comparison(name)
    equivalents = {
        "html5": "html", "css3": "css", "api rest": "apis rest",
        "consumo de apis rest": "apis rest", "desenvolvimento de apis rest": "apis rest",
        "integracao de apis rest": "apis rest", "integracao de apis": "apis rest",
        "ingles": "ingles tecnico",
    }
    return normalize_for_comparison(equivalents.get(name, equivalents.get(key, key)))


class ScoreCalculator(ScoreCalculatorInterface):
    """Deterministic ATS scoring, AI-score reconciliation, and evidence-based validation."""

    def _group_by_subrequirement(
        self, items: list[RequirementAnalysisItem]
    ) -> dict[str, list[RequirementAnalysisItem]]:
        """Group subrequirements (e.g. SQL, SELECT, JOIN) so they aren't scored twice."""
        groups: dict[str, list[RequirementAnalysisItem]] = {}
        for item in items:
            key = next(
                (grupo for grupo, membros in SUBREQUIREMENT_GROUPS.items() if item.item in membros),
                item.item,
            )
            groups.setdefault(key, []).append(item)
        return groups

    def _weighted_score(self, groups: dict[str, list[RequirementAnalysisItem]], job_level: JobLevel) -> int:
        total = sum(max(item.weight for item in group) for group in groups.values())
        points = sum(
            max(item.weight for item in group)
            * max(source_weight(job_level, EvidenceLevel(item.evidence_level)) for item in group)
            for group in groups.values()
        )
        return round(points / total * 100)

    def _cap_unreliable_perfect_score(self, score: int, item_count: int) -> int:
        if item_count < FEW_REQUIREMENTS_THRESHOLD and score == 100:
            return NEAR_PERFECT_SCORE_CAP
        return score

    def calculate_ats_score(
        self, items: list[RequirementAnalysisItem], valid_analysis: bool,
        job_level: JobLevel = JobLevel.NOT_PROVIDED,
    ) -> int:
        if not valid_analysis or not items:
            return 0

        groups = self._group_by_subrequirement(items)
        score = self._weighted_score(groups, job_level)
        return self._cap_unreliable_perfect_score(score, len(items))

    def _reconcile_requirement(
        self,
        req: AIRequirementAnalysis,
        local_by_key: dict[str, RequirementAnalysisItem],
        adjustments: list[str],
    ) -> AIRequirementAnalysis:
        local_item = local_by_key.get(_ai_requirement_key(req.item))
        if not local_item or req.status == local_item.status:
            return req

        previous_status = req.status
        reconciled = req.model_copy(update={
            "status": local_item.status,
            "evidence": local_item.resume_evidence,
            "rationale": f"Classification reconciled with local evidence: {local_item.evidence_level}.",
        })
        if local_item.evidence_level == EvidenceLevel.EDUCATIONAL.value:
            adjustments.append(f"{reconciled.item} rebaixado para evidência educacional")
        elif previous_status == "missing":
            adjustments.append(f"{reconciled.item} corrigido por evidência ou equivalência local")
        else:
            adjustments.append(f"{reconciled.item} conciliado com a força da evidência local")
        return reconciled

    def _filter_supported_gaps(self, gaps: list[str], requirements: list[AIRequirementAnalysis]) -> list[str]:
        not_gaps = {
            _ai_requirement_key(req.item)
            for req in requirements
            if req.status in {"found_with_evidence", "found_without_clear_context", "related_but_not_explicit"}
        }
        return [item for item in gaps if _ai_requirement_key(item) not in not_gaps]

    def _filter_unsupported_strengths(
        self, strengths: list[str], missing_items: set[str], adjustments: list[str]
    ) -> list[str]:
        kept = []
        for point in strengths:
            cited = [item for item in missing_items if normalize_for_comparison(item) in normalize_for_comparison(point)]
            if cited:
                adjustments.append(f"Ponto forte sem evidência removido: {', '.join(cited)}")
            else:
                kept.append(point)
        return kept

    def _relocate_unsupported_suggestions(
        self, suggestions: list[str], missing_items: set[str], next_steps: list[str], adjustments: list[str]
    ) -> list[str]:
        kept = []
        for suggestion in suggestions:
            cited = [item for item in missing_items if normalize_for_comparison(item) in normalize_for_comparison(suggestion)]
            if cited and re.search(r"\b(adicione|inclua|declare|destaque|reescreva)\b", normalize_for_comparison(suggestion)):
                next_steps.append(f"Estude ou crie um project real com {', '.join(cited)} antes de incluir como experiência.")
                adjustments.append(f"Sugestão sem evidência para {', '.join(cited)} movida para próximos passos")
            else:
                kept.append(suggestion)
        return kept

    def post_validate_ai_analysis(
        self, response: AIAnalysisResponse, local_result: AnalysisResult
    ) -> tuple[AIAnalysisResponse, list[str]]:
        """Reconcile external output with the traceable local inventory."""
        local_by_key = {_ai_requirement_key(i.item): i for i in local_result.requirement_analysis}
        adjustments: list[str] = []

        requirements = [
            self._reconcile_requirement(req, local_by_key, adjustments)
            for req in response.contextual_requirements
        ]
        gaps = self._filter_supported_gaps(response.gaps, requirements)

        missing_items = {
            i.item for i in local_result.requirement_analysis if i.evidence_level == EvidenceLevel.ABSENT.value
        }
        strengths = self._filter_unsupported_strengths(response.strengths, missing_items, adjustments)
        next_steps = list(response.next_steps)
        improvements = self._relocate_unsupported_suggestions(
            response.improvement_suggestions, missing_items, next_steps, adjustments
        )

        return response.model_copy(update={
            "contextual_requirements": requirements,
            "gaps": gaps,
            "strengths": strengths,
            "improvement_suggestions": improvements,
            "next_steps": list(dict.fromkeys(next_steps)),
        }), list(dict.fromkeys(adjustments))

    def _ai_weight(self, adjustments: int, qualidade_context: int | None, steps_fallback: int) -> float:
        weight = AI_WEIGHT_WITH_MANY_ADJUSTMENTS if adjustments >= LOW_ADJUSTMENTS_THRESHOLD else AI_WEIGHT_WITH_FEW_ADJUSTMENTS
        if (qualidade_context or 100) < LOW_CONTEXT_QUALITY_THRESHOLD:
            weight = min(weight, AI_WEIGHT_CAP_ON_LOW_CONTEXT)
        if steps_fallback:
            weight = max(MIN_AI_WEIGHT, weight - min(FALLBACK_PENALTY_CAP, steps_fallback * FALLBACK_PENALTY_PER_STEP))
        return weight

    def _apply_final_score_caps(
        self, final: int, local: int, ia: int, level: str, tem_experiencia: bool, hard_filters_ausentes: int,
    ) -> int:
        if local < LOW_LOCAL_SCORE_THRESHOLD and ia > HIGH_AI_SCORE_THRESHOLD:
            final = min(final, LOW_LOCAL_HIGH_AI_SCORE_CAP)
        if level in {JobLevel.MID_LEVEL.value, JobLevel.SENIOR.value} and not tem_experiencia:
            final = min(final, NO_EXPERIENCE_SENIOR_SCORE_CAP)
        if hard_filters_ausentes:
            final = min(final, max(
                HARD_FILTER_SCORE_FLOOR, HARD_FILTER_SCORE_BASE - hard_filters_ausentes * HARD_FILTER_PENALTY_PER_MISSING,
            ))
        return final

    def calculate_final_score(
        self, local: int, ia: int | None, confidence: int | None, adjustments: int,
        level: str, tem_experiencia: bool, keyword: int | None = None,
        hard_filters_ausentes: int = 0, qualidade_context: int | None = None,
        steps_fallback: int = 0,
    ) -> tuple[int, str]:
        if ia is None or (confidence or 0) < MIN_AI_CONFIDENCE:
            base = round(local * LOCAL_ONLY_WEIGHT + keyword * KEYWORD_ONLY_WEIGHT) if keyword is not None else local
            return base, "A IA não apresentou confiança suficiente; prevaleceram score local e cobertura ponderada de keywords."

        weight_ia = self._ai_weight(adjustments, qualidade_context, steps_fallback)
        weight_keyword = KEYWORD_WEIGHT_WHEN_PROVIDED if keyword is not None else 0
        weight_local = 1 - weight_ia - weight_keyword
        final = round(local * weight_local + ia * weight_ia + (keyword or 0) * weight_keyword)
        final = self._apply_final_score_caps(final, local, ia, level, tem_experiencia, hard_filters_ausentes)

        explanation = (
            f"Conciliação explicável: local {round(weight_local * 100)}%, "
            f"keywords {round(weight_keyword * 100)}% e IA {round(weight_ia * 100)}%; "
            f"confiança {confidence}%, correções {adjustments}, etapas com fallback {steps_fallback}, "
            f"hard filters missing_items {hard_filters_ausentes}."
        )
        return final, explanation


def calculate_ats_score(
    items: list[RequirementAnalysisItem], valid_analysis: bool,
    job_level: JobLevel = JobLevel.NOT_PROVIDED,
) -> int:
    return ScoreCalculator().calculate_ats_score(items, valid_analysis, job_level)


def post_validate_ai_analysis(
    response: AIAnalysisResponse, local_result: AnalysisResult
) -> tuple[AIAnalysisResponse, list[str]]:
    return ScoreCalculator().post_validate_ai_analysis(response, local_result)


def calculate_final_score(
    local: int, ia: int | None, confidence: int | None, adjustments: int,
    level: str, tem_experiencia: bool, keyword: int | None = None,
    hard_filters_ausentes: int = 0, qualidade_context: int | None = None,
    steps_fallback: int = 0,
) -> tuple[int, str]:
    return ScoreCalculator().calculate_final_score(
        local, ia, confidence, adjustments, level, tem_experiencia, keyword,
        hard_filters_ausentes, qualidade_context, steps_fallback,
    )
