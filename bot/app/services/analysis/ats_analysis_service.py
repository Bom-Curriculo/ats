"""Deterministic ATS pipeline and AI-enriched reconciliation, composed from focused collaborators."""

import re

from app.providers.base import AIProvider
from app.models.analysis import (
    DetailedAnalysis,
    ResumeEvidence,
    PrivacyInformation,
    AnalysisResult,
    AnalysisRequest,
)
from app.services.parsing.interfaces import SectionExtractorInterface, ResumeInventoryBuilderInterface
from app.services.parsing.section_extractor import SectionExtractor
from app.services.parsing.resume_inventory import ResumeInventoryBuilder
from app.services.analysis.interfaces import (
    AtsAnalysisServiceInterface,
    FactBankBuilderInterface,
    RequirementExtractorInterface,
    ScoreCalculatorInterface,
    SuggestionEngineInterface,
)
from app.services.analysis.fact_bank import FactBankBuilder
from app.services.matching.interfaces import (
    JobLevel,
    KeywordReportBuilderInterface,
    RequirementGroupBuilderInterface,
    TechnicalEquivalenceResolverInterface,
)
from app.services.matching.keyword_report import KeywordReportBuilder
from app.services.matching.requirement_groups import RequirementGroupBuilder
from app.services.matching.technical_equivalences import TechnicalEquivalenceResolver
from app.services.ai.interfaces import AIPipelineOrchestratorInterface, StructuredAIAnalysisValidatorInterface
from app.services.ai.ai_orchestrator import AIPipelineOrchestrator
from app.services.normalization.interfaces import TextNormalizerInterface, JobNormalizerInterface
from app.services.normalization.text_normalizer import normalize_for_comparison, TextNormalizer
from app.services.normalization.job_normalizer import JobNormalizer
from app.services.privacy.interfaces import SanitizerInterface
from app.services.privacy.sanitizer import PrivacySanitizer
from app.services.ai.structured_ai_analysis import StructuredAIAnalysisValidator
from app.services.analysis.requirement_extractor import RequirementExtractor
from app.services.analysis.score_calculator import ScoreCalculator
from app.services.analysis.suggestion_engine import SuggestionEngine

# Resume sections that constitute usable practical evidence; if the parser is
# unsure about section boundaries AND none of these were found, the score is
# unreliable.
EVIDENCE_BEARING_SECTIONS = (
    "professional_experience", "projects", "academic_projects", "freelance", "open_source", "residencies",
)
LOW_CONFIDENCE_SCORE_CAP = 70

# A long job post that yields very few extracted requirements suggests
# extraction failed silently; cap the score rather than trust it.
SPARSE_JOB_TEXT_MIN_LENGTH = 300
SPARSE_JOB_MIN_REQUIREMENTS = 3
SPARSE_REQUIREMENTS_SCORE_CAP = 60

MAX_AI_SUGGESTIONS = 10


class AtsAnalysisService(AtsAnalysisServiceInterface):
    """Facade composing requirement extraction, scoring, and suggestions into one pipeline."""

    def __init__(
        self,
        requirement_extractor: RequirementExtractorInterface | None = None,
        score_calculator: ScoreCalculatorInterface | None = None,
        suggestion_engine: SuggestionEngineInterface | None = None,
        sanitizer: SanitizerInterface | None = None,
        text_normalizer: TextNormalizerInterface | None = None,
        job_normalizer: JobNormalizerInterface | None = None,
        technical_equivalence_resolver: TechnicalEquivalenceResolverInterface | None = None,
        section_extractor: SectionExtractorInterface | None = None,
        resume_inventory_builder: ResumeInventoryBuilderInterface | None = None,
        fact_bank_builder: FactBankBuilderInterface | None = None,
        requirement_group_builder: RequirementGroupBuilderInterface | None = None,
        keyword_report_builder: KeywordReportBuilderInterface | None = None,
        ai_pipeline_orchestrator: AIPipelineOrchestratorInterface | None = None,
        structured_ai_analysis_validator: StructuredAIAnalysisValidatorInterface | None = None,
    ) -> None:
        self._requirements = requirement_extractor or RequirementExtractor()
        self._scores = score_calculator or ScoreCalculator()
        self._suggestions = suggestion_engine or SuggestionEngine()
        self._sanitizer = sanitizer or PrivacySanitizer()
        self._text_normalizer = text_normalizer or TextNormalizer()
        self._job_normalizer = job_normalizer or JobNormalizer()
        self._job_levels = technical_equivalence_resolver or TechnicalEquivalenceResolver()
        self._sections = section_extractor or SectionExtractor()
        self._inventory = resume_inventory_builder or ResumeInventoryBuilder()
        self._fact_bank = fact_bank_builder or FactBankBuilder()
        self._requirement_groups = requirement_group_builder or RequirementGroupBuilder()
        self._keyword_reports = keyword_report_builder or KeywordReportBuilder()
        self._ai_pipeline = ai_pipeline_orchestrator or AIPipelineOrchestrator()
        self._structured_ai_validator = structured_ai_analysis_validator or StructuredAIAnalysisValidator()

    def _sanitize_inputs(self, request: AnalysisRequest):
        resume_normalized = self._text_normalizer.normalize_resume_text(request.resume_text)
        job_normalized = self._text_normalizer.normalize_resume_text(request.job_text)
        sanitization_resume = self._sanitizer.sanitize(resume_normalized)
        sanitization_job = self._sanitizer.sanitize(job_normalized)
        urls_sources = "\n".join(source.url for source in request.resume_sources if source.url)
        sanitization_sources = self._sanitizer.sanitize(urls_sources) if urls_sources else None
        return sanitization_resume, sanitization_job, sanitization_sources

    def _resolve_job_level(self, request: AnalysisRequest, job_text_original: str) -> JobLevel:
        detected_level = self._job_levels.detect_job_level(job_text_original)
        if not request.job_level:
            return detected_level
        try:
            return JobLevel(normalize_for_comparison(request.job_level))
        except ValueError:
            return detected_level

    def _apply_low_confidence_cap(self, score: int, low_confidence_sections: list[str], sections: dict[str, str]) -> int:
        has_evidence_bearing_section = any(key in sections for key in EVIDENCE_BEARING_SECTIONS)
        if low_confidence_sections and not has_evidence_bearing_section:
            return min(score, LOW_CONFIDENCE_SCORE_CAP)
        return score

    def _apply_sparse_requirements_cap(
        self, score: int, job_text_sanitized: str, items: list, alerts: list[str], issues: list[str],
    ) -> int:
        is_sparse = len(job_text_sanitized) >= SPARSE_JOB_TEXT_MIN_LENGTH and len(items) < SPARSE_JOB_MIN_REQUIREMENTS
        if not is_sparse:
            return score
        alert = "Poucos requisitos extraídos da vaga; a pontuação foi limitada por segurança."
        alerts.append(alert)
        issues.append(alert)
        return min(score, SPARSE_REQUIREMENTS_SCORE_CAP)

    def _build_detailed_analysis(
        self, items: list, found_items: list[str], missing_items: list[str], blockers: list[str],
    ) -> DetailedAnalysis:
        return DetailedAnalysis(
            found_required_requirements=[
                i.item for i in items if i.category == "requirement_obrigatorio" and i.item in found_items
            ],
            missing_required_requirements=[
                i.item for i in items if i.category == "requirement_obrigatorio" and i.item in missing_items
            ],
            found_differentials=[
                i.item for i in items if i.category == "differential" and i.item in found_items
            ],
            missing_differentials=[
                i.item for i in items if i.category == "differential" and i.item in missing_items
            ],
            found_technologies=[
                i.item for i in items if i.type == "technology" and i.item in found_items
            ],
            missing_technologies=[
                i.item for i in items if i.type == "technology" and i.item in missing_items
            ],
            possible_blockers=blockers,
        )

    def _build_sanitization_summary(self, sanitization_resume, sanitization_sources) -> dict:
        source_items = sanitization_sources.items_removed if sanitization_sources else []
        source_links = sanitization_sources.links_detected_by_type if sanitization_sources else {}
        return {
            "sensitive_data_detected": bool(sanitization_resume.items_removed or source_items),
            "removed_categories": list(dict.fromkeys(sanitization_resume.items_removed + source_items)),
            "category_count": len(set(sanitization_resume.items_removed + source_items)),
            "links_detected_by_type": {
                key: sanitization_resume.links_detected_by_type.get(key, 0) + source_links.get(key, 0)
                for key in set(sanitization_resume.links_detected_by_type) | set(source_links)
            },
            "safe_note": "Valores sensíveis foram substituídos antes da análise externa e não são retornados.",
        }

    def _build_relevance_evaluation(self, job: dict, job_level: JobLevel) -> dict:
        return {
            "title_detectado": job.get("title", ""),
            "company": job.get("company", ""),
            "area": job.get("area", ""),
            "level": job_level.value,
            "modality": job.get("modality", ""),
            "location": job.get("localidade", ""),
            "accepts_no_experience": bool(job.get("accepts_no_experience")),
        }

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Run the pipeline without retaining source text."""

        job_text_original = request.job_text
        sanitization_resume, sanitization_job, sanitization_sources = self._sanitize_inputs(request)
        resume_text_sanitized = sanitization_resume.text_sanitized
        job_text_sanitized = sanitization_job.text_sanitized

        job = self._job_normalizer.normalize_job_text(job_text_sanitized)
        job_level = self._resolve_job_level(request, job_text_original)

        parser_sections = self._sections.analyze(resume_text_sanitized)
        sections = parser_sections.sections

        inventory = self._inventory.build(resume_text_sanitized, sections)
        fact_bank = self._fact_bank.build(sections)

        requirements = self._requirements.extract_job_requirements(job)
        items = self._requirements.compare_resume_to_job(resume_text_sanitized, sections, requirements)
        requirement_groups, grouped_score, score_by_group = self._requirement_groups.build(items, job_level.value, job_text_sanitized)
        keyword_report, keyword_score, present_keywords, missing_keywords_weighted = self._keyword_reports.build(
            items, job_text_sanitized, resume_text_sanitized, str(job.get("title", "")))
        valid_analysis, alerts = self._suggestions.is_valid_input(resume_text_sanitized, job_text_sanitized)
        blockers = self._suggestions.detect_possible_blockers(resume_text_sanitized, job_text_sanitized)
        blockers.extend(keyword_report.hard_filter_alerts)
        evidence_items_dict = self._sections.detect_evidence(resume_text_sanitized, sections)
        local_suggestions = self._suggestions.generate_local_suggestions(
            items, evidence_items_dict, blockers, job_text_sanitized
        )

        found_items = [i.item for i in items if i.status in {"found_with_evidence", "found_without_clear_context"}]
        missing_items = [i.item for i in items if i.status not in {"found_with_evidence", "found_without_clear_context"}]

        inventory["habilidades_nao_exigidas_pela_job"] = [
            h for h in inventory["habilidades_detectadas"] if h not in {i.item for i in items}
        ]

        details = self._build_detailed_analysis(items, found_items, missing_items, blockers)

        score = grouped_score if valid_analysis else 0
        score = self._apply_low_confidence_cap(score, parser_sections.low_confidence_sections, sections)

        issues = self._requirements.detect_missing_sections(resume_text_sanitized)
        score = self._apply_sparse_requirements_cap(score, job_text_sanitized, items, alerts, issues)

        suggestions = (
            local_suggestions.recommended_adjustments
            + local_suggestions.technical_gaps
            + local_suggestions.attention_points
            + local_suggestions.next_steps
        )

        return AnalysisResult(
            valid_analysis=valid_analysis,
            input_alerts=alerts,
            ats_score=score,
            matched_keywords=found_items,
            missing_keywords=missing_items,
            resume_inventory=inventory,
            requirement_analysis=items,
            detailed_analysis=details,
            evidence_items=ResumeEvidence(**evidence_items_dict),
            detected_issues=issues,
            suggestions=suggestions,
            detailed_suggestions=local_suggestions,
            matching_explanation="O inventário lista todas as habilidades detectadas; o matching e o score usam somente requisitos reais desta vaga, ponderados por categoria e força da evidência.",
            generated_summary=f"Análise {'válida' if valid_analysis else 'inválida'}: {score}% de compatibilidade ponderada.",
            ai_provider="sem_ia",
            ai_model=None,
            job_level=job_level.value,
            keyword_report=keyword_report,
            score_keyword_coverage=keyword_score,
            weighted_present_keywords=present_keywords,
            weighted_missing_keywords=missing_keywords_weighted,
            keyword_coverage_explanation="Cobertura ponderada por categoria; hard filters geram alertas fora do score.",
            fact_bank=fact_bank,
            relevance_evaluation=self._build_relevance_evaluation(job, job_level),
            evidence_matrix=[{"item": i.item, "source": i.evidence_source, "level": i.evidence_level} for i in items],
            prioritized_gaps=[{"item": i.item, "weight": i.weight} for i in items if i.status == "missing"],
            ats_diagnostics={"score_local": score, "score_keyword_coverage": keyword_score},
            final_score_factors={"score_local": score, "score_keyword_coverage": keyword_score},
            final_score_alerts=keyword_report.hard_filter_alerts,
            requirement_groups=requirement_groups,
            score_by_group=score_by_group,
            grouped_semantic_score=grouped_score,
            parser_warnings=parser_sections.warnings,
            detected_sections=[x for x in sections if x != "outros"],
            low_confidence_sections=parser_sections.low_confidence_sections,
            evidence_source_summary=self._fact_bank.summarize_sources(fact_bank),
            sanitization_summary=self._build_sanitization_summary(sanitization_resume, sanitization_sources),
            recommended_final_score=score,
            final_score_explanation="Sem análise externa válida, o score final recomendado é igual à pontuação ATS local.",
        )

    async def _run_ai_analysis(self, safe: AnalysisRequest, result: AnalysisResult, provider: AIProvider):
        """Prefer the multi-step pipeline; fall back to the single-shot validator when it's unreliable."""
        task_responses = getattr(provider, "task_responses", None)
        supports_pipeline = task_responses is None or bool(task_responses)

        if not supports_pipeline:
            return None, await self._structured_ai_validator.run(safe, result, provider, self._sanitizer)

        ai_pipeline, ai_analysis = await self._ai_pipeline.run(safe, result, provider)
        if len(ai_pipeline.fallback_steps) >= 3:
            ai_analysis = await self._structured_ai_validator.run(safe, result, provider, self._sanitizer)
        return ai_pipeline, ai_analysis

    def _deduplicate_ai_suggestions(self, candidates: list[str]) -> list[str]:
        deduplicated: list[str] = []
        seen: set[str] = set()
        for suggestion in candidates:
            key = re.sub(
                r"\b(select|join|where|insert|update|delete|branches?|pull requests?|code review)\b",
                "grupo", normalize_for_comparison(suggestion),
            )
            if key not in seen:
                seen.add(key)
                deduplicated.append(suggestion)
            if len(deduplicated) == MAX_AI_SUGGESTIONS:
                break
        return deduplicated

    def _local_fallback_result(self, result: AnalysisResult, removed_items: list[str]) -> AnalysisResult:
        return result.model_copy(
            update={
                "local_fallback_used": True,
                "recommended_final_score": result.ats_score,
                "final_score_explanation": "A IA falhou ou retornou schema inválido; foi mantida a pontuação ATS local.",
                "privacy": PrivacyInformation(
                    sensitive_data_detected=bool(removed_items),
                    items_removed_before_ai=removed_items,
                    ai_text_was_sanitized=True,
                ),
            }
        )

    def _build_ai_enriched_update(
        self, result: AnalysisResult, provider: AIProvider, ai_analysis, ai_pipeline,
        validation_adjustments: list[str], removed_items: list[str],
    ) -> dict:
        ai_suggestions = self._deduplicate_ai_suggestions(ai_analysis.improvement_suggestions + ai_analysis.next_steps)
        final_score, final_explanation = self._scores.calculate_final_score(
            result.ats_score,
            ai_analysis.ai_suggested_score,
            ai_analysis.confidence,
            len(validation_adjustments),
            result.job_level,
            bool(result.evidence_items and result.evidence_items.professional_experience),
            result.score_keyword_coverage,
            len(result.keyword_report.hard_filter_alerts) if result.keyword_report else 0,
            ai_analysis.ai_context_quality,
            len(ai_pipeline.fallback_steps) if ai_pipeline else 0,
        )

        return {
            "generated_summary": ai_analysis.contextual_summary,
            "suggestions": ai_suggestions or result.suggestions,
            "ai_provider": provider.name,
            "ai_model": provider.model,
            "ai_analysis": ai_analysis,
            "ai_suggested_score": ai_analysis.ai_suggested_score,
            "ai_score_rationale": ai_analysis.ai_score_rationale,
            "ai_confidence": ai_analysis.confidence,
            "local_fallback_used": False,
            "ai_validation_applied": True,
            "ai_validation_adjustments": validation_adjustments,
            "recommended_final_score": final_score,
            "final_score_explanation": final_explanation,
            "contextual_requirements": ai_analysis.contextual_requirements,
            "contextual_gaps": ai_analysis.gaps,
            "next_steps": ai_analysis.next_steps,
            "anti_fabrication_alerts": ai_analysis.anti_fabrication_alerts,
            "ai_roles": ai_analysis.ai_roles or ["avaliadora contextual", "auditora de lacunas", "revisora anti-alucinação"],
            "ai_context_quality": ai_analysis.ai_context_quality,
            "relevance_evaluation": ai_analysis.relevance_evaluation or result.relevance_evaluation,
            "evidence_matrix": ai_analysis.evidence_matrix or result.evidence_matrix,
            "prioritized_gaps": ai_analysis.prioritized_gaps or result.prioritized_gaps,
            "safe_rewrite_suggestions": ai_analysis.safe_rewrite_suggestions,
            "ats_diagnostics": ai_analysis.ats_diagnostics or result.ats_diagnostics,
            "contextual_ai_score": ai_analysis.contextual_ai_score,
            "final_score_factors": {
                "score_local": result.ats_score, "score_keywords": result.score_keyword_coverage or 0,
                "score_ia": ai_analysis.ai_suggested_score or 0, "ai_confidence": ai_analysis.confidence,
                "correcoes_ia": len(validation_adjustments), "fallback_steps": len(ai_pipeline.fallback_steps) if ai_pipeline else 0,
            },
            "ai_pipeline": ai_pipeline,
            "executed_ai_steps": ai_pipeline.executed_steps if ai_pipeline else [],
            "fallback_ai_steps": ai_pipeline.fallback_steps if ai_pipeline else [],
            "job_relevant_evidence": ai_pipeline.relevant_evidence if ai_pipeline else [],
            "ai_job_classification": ai_pipeline.job_classification if ai_pipeline else None,
            "contextual_requirement_evaluations": ai_pipeline.requirement_evaluations if ai_pipeline else [],
            "ai_pipeline_confidence": ai_pipeline.pipeline_confidence if ai_pipeline else None,
            "sanitized_pipeline_errors": [x["safe_message"] for x in ai_pipeline.fallback_details] if ai_pipeline else [],
            "pipeline_fallback_details": ai_pipeline.fallback_details if ai_pipeline else [],
            "privacy": PrivacyInformation(
                sensitive_data_detected=bool(removed_items),
                items_removed_before_ai=removed_items,
                ai_text_was_sanitized=True,
            ),
        }

    async def analyze_with_ai(
        self,
        request: AnalysisRequest,
        provider: AIProvider,
        propagate_provider_error: bool = False,
    ) -> AnalysisResult:
        result = self.analyze(request)

        resume_sanitized = self._sanitizer.sanitize(request.resume_text)
        job_sanitized = self._sanitizer.sanitize(request.job_text)
        removed_items = list(dict.fromkeys(resume_sanitized.items_removed + job_sanitized.items_removed))

        safe = request.model_copy(
            update={
                "resume_text": resume_sanitized.text_sanitized,
                "job_text": job_sanitized.text_sanitized,
                "resume_sources": [],
            }
        )

        ai_pipeline, ai_analysis = None, None
        try:
            ai_pipeline, ai_analysis = await self._run_ai_analysis(safe, result, provider)
        except Exception:
            if propagate_provider_error:
                raise

        if ai_analysis is None:
            return self._local_fallback_result(result, removed_items)

        ai_analysis, validation_adjustments = self._scores.post_validate_ai_analysis(ai_analysis, result)
        update = self._build_ai_enriched_update(
            result, provider, ai_analysis, ai_pipeline, validation_adjustments, removed_items
        )
        return result.model_copy(update=update)


def analyze_resume(request: AnalysisRequest, service: AtsAnalysisServiceInterface | None = None) -> AnalysisResult:
    return (service or AtsAnalysisService()).analyze(request)


async def analyze_resume_with_ai(
    request: AnalysisRequest,
    provider: AIProvider,
    propagate_provider_error: bool = False,
    service: AtsAnalysisServiceInterface | None = None,
) -> AnalysisResult:
    return await (service or AtsAnalysisService()).analyze_with_ai(request, provider, propagate_provider_error)
