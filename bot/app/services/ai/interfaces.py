from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

from app.models.resume_analysis import ResumeAnalysisResult, SkillItem

if TYPE_CHECKING:
    from app.providers.base import AIProvider


class ResumeAnalysisManagerInterface(ABC):
    """Selects, calls, and safely falls back across configured AI providers."""

    @abstractmethod
    def get_provider_chain(self) -> list[str]:
        ...

    @abstractmethod
    def is_provider_configured(self, name: str) -> bool:
        ...

    @abstractmethod
    async def extract_resume(
        self,
        resume_text: str,
        factory: Callable[[str], AIProvider] | None = None,
        linkedin_text: str | None = None,
        github_url: str | None = None,
        portfolio_url: str | None = None,
        additional_skills: list[SkillItem] | None = None,
    ) -> ResumeAnalysisResult:
        ...
