from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

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


ResumeContentRejectionReason = Literal["empty", "too_short", "low_content_diversity"]


@dataclass(frozen=True)
class ResumeContentValidation:
    is_valid: bool
    reason: ResumeContentRejectionReason | None = None


class ResumeContentValidatorInterface(ABC):
    """Reject empty, too-short, or low-effort ("troll") resume text before analysis.

    Applies to resume text from any source (inline or extracted from a PDF/DOCX
    file) — a scanned image with no extractable text, a one-line placeholder,
    or repeated junk content should never reach the AI as if it were a real resume.
    """

    @abstractmethod
    def validate(self, text: str) -> ResumeContentValidation:
        ...
