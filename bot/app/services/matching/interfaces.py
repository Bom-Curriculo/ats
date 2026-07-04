import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from app.models.analysis import RequirementGroup, RequirementAnalysisItem, ItemKeyword, KeywordReport, FactBank
from app.models.ai_pipeline import SelectedEvidence
from app.services.privacy.interfaces import SanitizerInterface


@dataclass(frozen=True)
class Technology:
    name: str
    category: str
    aliases: tuple[str, ...]


class EvidenceLevel(StrEnum):
    STRONG_PRACTICAL = "strong_practical_evidence"
    PARTIAL_PRACTICAL = "partial_practical_evidence"
    EDUCATIONAL = "educational_evidence"
    STANDALONE_SKILL = "standalone_skill_evidence"
    RELATED = "related_evidence"
    ABSENT = "no_evidence"


class JobLevel(StrEnum):
    INTERNSHIP = "estagio"
    TRAINEE = "trainee"
    JUNIOR = "junior"
    MID_LEVEL = "pleno"
    SENIOR = "senior"
    NOT_PROVIDED = "not_provided"


class InferenceStrength(StrEnum):
    STRONG = "implicacao_forte"
    LIKELY = "relacao_provavel"
    WEAK = "relacao_fraca"


@dataclass(frozen=True)
class Inference:
    origin: str
    target: str
    strength: InferenceStrength
    requires_context: tuple[str, ...] = ()


class TechnicalMatcherInterface(ABC):
    """Boundary-aware technical-term matching over normalized text."""

    @abstractmethod
    def find_alias(self, text: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
        ...

    @abstractmethod
    def contains_alias(self, text: str, aliases: tuple[str, ...], name: str | None = None) -> bool:
        ...


class TechnologyCatalogInterface(ABC):
    """Lookup over the static technology/skill catalog."""

    @abstractmethod
    def find(self, name: str) -> Technology | None:
        ...


class TechnicalEquivalenceResolverInterface(ABC):
    """Job-level detection, evidence weighting, and technology-inference lookups."""

    @abstractmethod
    def detect_job_level(self, text: str) -> JobLevel:
        ...

    @abstractmethod
    def source_weight(self, level: JobLevel, evidence: EvidenceLevel) -> float:
        ...

    @abstractmethod
    def public_status(self, evidence: EvidenceLevel) -> str:
        ...

    @abstractmethod
    def inferences_for(self, target: str) -> tuple[Inference, ...]:
        ...


class RequirementGroupBuilderInterface(ABC):
    """Group alternative/complementary requirements so they aren't scored twice."""

    @abstractmethod
    def build(
        self, items: list[RequirementAnalysisItem], level_text: str, job_text: str = ""
    ) -> tuple[list[RequirementGroup], int, dict[str, int]]:
        ...


class KeywordReportBuilderInterface(ABC):
    """Group requirement items into weighted keyword categories and score coverage."""

    @abstractmethod
    def build(
        self, items: list[RequirementAnalysisItem], job: str, resume: str, title: str = ""
    ) -> tuple[KeywordReport, int, list[ItemKeyword], list[ItemKeyword]]:
        ...


class EvidenceSelectorInterface(ABC):
    """Select and rank the fact-bank evidence most relevant to a job's requirements."""

    @abstractmethod
    def select(
        self, fact_bank: FactBank | None, requirements: list, keyword_report: KeywordReport | None,
        seniority: str = "not_provided", limit: int = 20, sanitizer: SanitizerInterface | None = None,
    ) -> list[SelectedEvidence]:
        ...
