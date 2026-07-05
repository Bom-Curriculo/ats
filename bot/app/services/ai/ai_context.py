from app.models.analysis import AnalysisResult, AnalysisRequest
from app.services.ai.interfaces import AIContextBuilderInterface
from app.services.privacy.interfaces import SanitizerInterface
from app.services.privacy.sanitizer import PrivacySanitizer


class AIContextBuilder(AIContextBuilderInterface):
    """Build a compact provider context without the raw payload."""

    def _summarize(self, text: str, sanitizer: SanitizerInterface, limit: int = 1600) -> str:
        safe = sanitizer.sanitize(text).text_sanitized
        lines = [line.strip() for line in safe.splitlines() if line.strip()]
        return "\n".join(lines)[:limit]

    def build(
        self, request: AnalysisRequest, result: AnalysisResult, sanitizer: SanitizerInterface | None = None
    ) -> dict:
        sanitizer = sanitizer or PrivacySanitizer()
        requirements = [item.model_dump() for item in result.requirement_analysis]
        return {
            "summary_resume_sanitized": self._summarize(request.resume_text, sanitizer),
            "summary_job_sanitized": self._summarize(request.job_text, sanitizer),
            "job_level": result.job_level,
            "detected_job_title": result.relevance_evaluation.title_detectado if result.relevance_evaluation else None,
            "extracted_requirements": [r["item"] for r in requirements],
            "requirements_by_importance": requirements,
            "relevant_inventory": result.resume_inventory or {},
            "fact_bank": result.fact_bank.model_dump() if result.fact_bank else None,
            "evidence_items_by_requirement": [
                {"item": r["item"], "source": r["evidence_source"], "level": r["evidence_level"]}
                for r in requirements
            ],
            "local_gaps": result.missing_keywords,
            "local_strengths": result.matched_keywords,
            "keyword_report": result.keyword_report.model_dump() if result.keyword_report else None,
            "privacy_alerts": ["Content sanitized; do not reproduce or infer personal data."],
            "anti_fabrication_rules": [
                "A course is never practical experience.",
                "An isolated skill is never practical.",
                "A project is evidence of a project, not employment.",
                "Absence becomes a gap or a study/project suggestion.",
            ],
        }
