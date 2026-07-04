from abc import ABC, abstractmethod

from app.models.analysis import (
    AnalysisRequest,
    AnalysisResult,
    DetailedSuggestions,
    FactBank,
    RequirementAnalysisItem,
)
from app.models.ai_analysis import AIAnalysisResponse


class FactBankBuilderInterface(ABC):
    """Build the traceable, source-attributed fact bank from resume sections."""

    @abstractmethod
    def build(self, sections: dict[str, str]) -> FactBank:
        ...

    @abstractmethod
    def summarize_sources(self, fact_bank: FactBank) -> dict[str, int]:
        ...


class RequirementExtractorInterface(ABC):
    """Extract a job's requirements from the catalog and match them against a resume."""

    @abstractmethod
    def extract_job_requirements(self, job_estruturada: dict[str, str | list[str]]) -> list:
        ...

    @abstractmethod
    def extract_weighted_relevant_keywords(self, text_job: str, limite: int = 40) -> list:
        ...

    @abstractmethod
    def extract_relevant_keywords(self, text_job: str, limite: int = 40) -> list[str]:
        ...

    @abstractmethod
    def detect_missing_sections(self, resume_text: str) -> list[str]:
        ...

    @abstractmethod
    def compare_resume_to_job(
        self, resume: str, sections: dict[str, str], requirements: list
    ) -> list[RequirementAnalysisItem]:
        ...


class ScoreCalculatorInterface(ABC):
    """Deterministic ATS scoring, AI-score reconciliation, and evidence-based validation."""

    @abstractmethod
    def calculate_ats_score(
        self, items: list[RequirementAnalysisItem], valid_analysis: bool, job_level=None,
    ) -> int:
        ...

    @abstractmethod
    def post_validate_ai_analysis(
        self, response: AIAnalysisResponse, local_result: AnalysisResult
    ) -> tuple[AIAnalysisResponse, list[str]]:
        ...

    @abstractmethod
    def calculate_final_score(
        self, local: int, ia: int | None, confidence: int | None, adjustments: int,
        level: str, tem_experiencia: bool, keyword: int | None = None,
        hard_filters_ausentes: int = 0, qualidade_context: int | None = None,
        steps_fallback: int = 0,
    ) -> tuple[int, str]:
        ...


class SuggestionEngineInterface(ABC):
    """Local, evidence-bound suggestions, gap prioritization, and input sanity checks."""

    @abstractmethod
    def is_valid_input(self, resume: str, job: str) -> tuple[bool, list[str]]:
        ...

    @abstractmethod
    def detect_possible_blockers(self, resume: str, job: str) -> list[str]:
        ...

    @abstractmethod
    def generate_local_suggestions(
        self,
        items: list[RequirementAnalysisItem],
        evidence_items: dict[str, bool],
        impeditivos: list[str],
        job: str,
    ) -> DetailedSuggestions:
        ...


class AtsAnalysisServiceInterface(ABC):
    """Facade composing requirement extraction, scoring, and suggestions into one pipeline."""

    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        ...

    @abstractmethod
    async def analyze_with_ai(
        self, request: AnalysisRequest, provider, propagate_provider_error: bool = False
    ) -> AnalysisResult:
        ...
