"""Backward-compatible facade over `app.services.analysis`.

The deterministic ATS pipeline was split into focused collaborators
(`RequirementExtractor`, `ScoreCalculator`, `SuggestionEngine`) composed by
`AtsAnalysisService`. This module re-exports the previous flat function API
so existing imports keep working unchanged.
"""

from app.services.analysis.ats_analysis_service import (
    AtsAnalysisService,
    analyze_resume,
    analyze_resume_with_ai,
)
from app.services.analysis.requirement_extractor import (
    Keyword,
    RequirementExtractor,
    compare_resume_to_job,
    detect_missing_sections,
    extract_job_requirements,
    extract_relevant_keywords,
    extract_weighted_relevant_keywords,
    normalize_text,
)
from app.services.analysis.score_calculator import (
    ScoreCalculator,
    calculate_ats_score,
    calculate_final_score,
    post_validate_ai_analysis,
)
from app.services.analysis.suggestion_engine import (
    SuggestionEngine,
    detect_possible_blockers,
    generate_local_suggestions,
)

__all__ = [
    "AtsAnalysisService",
    "Keyword",
    "RequirementExtractor",
    "ScoreCalculator",
    "SuggestionEngine",
    "analyze_resume",
    "analyze_resume_with_ai",
    "calculate_ats_score",
    "calculate_final_score",
    "compare_resume_to_job",
    "detect_missing_sections",
    "detect_possible_blockers",
    "extract_job_requirements",
    "extract_relevant_keywords",
    "extract_weighted_relevant_keywords",
    "generate_local_suggestions",
    "normalize_text",
    "post_validate_ai_analysis",
]
