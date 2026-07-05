from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

from app.models.analysis import ResumeEvidence


@dataclass
class SectionParserResult:
    sections: dict[str, str]
    confidence_by_section: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    low_confidence_sections: list[str] = field(default_factory=list)


class SectionExtractorInterface(ABC):
    """Bilingual (PT/EN) resume section extraction."""

    @abstractmethod
    def analyze(self, text: str) -> SectionParserResult:
        ...

    @abstractmethod
    def extract_sections(self, text: str) -> dict[str, str]:
        ...

    @abstractmethod
    def detect_evidence(self, text: str, sections: dict[str, str]) -> ResumeEvidence:
        ...


class ResumeInventoryBuilderInterface(ABC):
    """Detect which technology/skill categories are present in a resume."""

    @abstractmethod
    def build(self, text: str, sections: dict[str, str] | None = None) -> dict[str, list[str]]:
        ...


class ResumeEntityParserInterface(ABC):
    """Parse projects and generic evidence blocks from classified resume sections."""

    @abstractmethod
    def extract_projects(self, text: str, *, source_type: str = "project") -> list[dict]:
        ...

    @abstractmethod
    def section_block(self, text: str, source: str, confidence: int = 90) -> list[dict]:
        ...


PayloadFormat = Literal["json", "laravel"]


@dataclass(frozen=True)
class ParsedRabbitMQPayload:
    format: PayloadFormat
    data: dict[str, Any]


class RabbitMQPayloadParserInterface(ABC):
    """Recognize clean JSON or a legacy serialized Laravel job payload."""

    @abstractmethod
    def parse(self, body: bytes | str) -> ParsedRabbitMQPayload:
        ...


class ResumeFileFetcherInterface(ABC):
    """Download a resume/LinkedIn file reference over HTTP and extract its text."""

    @abstractmethod
    async def fetch_and_extract_text(self, url: str) -> str:
        ...
