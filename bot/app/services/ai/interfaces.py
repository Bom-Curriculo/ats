from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

from app.models.analysis import AnalysisRequest, AnalysisResult
from app.models.ai_analysis import AIAnalysisResponse
from app.models.ai_pipeline import AIJobClassification, AIPipelineResult
from app.services.privacy.interfaces import SanitizerInterface

if TYPE_CHECKING:
    from app.providers.base import AIProvider


class AIContextBuilderInterface(ABC):
    """Build a compact provider context without the raw payload."""

    @abstractmethod
    def build(
        self, request: AnalysisRequest, result: AnalysisResult, sanitizer: SanitizerInterface | None = None
    ) -> dict:
        ...


class AIPipelinePromptsInterface(ABC):
    """Focused prompts that never include the complete fact bank."""

    @abstractmethod
    def job_classification(self, summarized_job: str, local_context: dict, schema: dict) -> str:
        ...

    @abstractmethod
    def contextual_evaluation(
        self, classification: dict, requirements: list[dict], evidence_items: list[dict], schema: dict
    ) -> str:
        ...

    @abstractmethod
    def safe_suggestions(self, evaluations: list[dict], gaps: list[dict], schema: dict) -> str:
        ...


class AIPipelineOrchestratorInterface(ABC):
    """Run the structured, multi-step AI pipeline with per-step local fallback."""

    @abstractmethod
    def prepare_context(self, request: AnalysisRequest, result: AnalysisResult) -> dict:
        ...

    @abstractmethod
    async def classify_job(
        self, context: dict, result: AnalysisResult, provider: AIProvider
    ) -> tuple[AIJobClassification, bool, dict | None]:
        ...

    @abstractmethod
    async def run(
        self, request: AnalysisRequest, result: AnalysisResult, provider: AIProvider
    ) -> tuple[AIPipelineResult, AIAnalysisResponse]:
        ...


class StructuredAIAnalysisValidatorInterface(ABC):
    """Validate the external AI boundary; failures become a controlled local fallback."""

    @abstractmethod
    async def run(
        self, safe_request: AnalysisRequest, local_result: AnalysisResult, provider: AIProvider,
        sanitizer: SanitizerInterface | None = None,
    ) -> AIAnalysisResponse | None:
        ...


class AIManagerInterface(ABC):
    """Selects, calls, and safely falls back across configured AI providers."""

    @abstractmethod
    def get_provider_chain(self) -> list[str]:
        ...

    @abstractmethod
    def is_provider_configured(self, name: str) -> bool:
        ...

    @abstractmethod
    async def run_analysis_with_fallback(
        self, request: AnalysisRequest, factory: Callable[[str], AIProvider] | None = None
    ) -> AnalysisResult:
        ...
