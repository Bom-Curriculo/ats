from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SanitizationResult:
    text_sanitized: str
    items_removed: list[str]
    links_detected_by_type: dict[str, int] = field(default_factory=dict)

    @property
    def sensitive_data_detected(self) -> bool:
        return bool(self.items_removed)


class SanitizerInterface(ABC):
    """Strip PII, secrets, and sensitive URLs before text crosses an external boundary."""

    @abstractmethod
    def sanitize(
        self, text: str, *, remove_links: bool = True, remove_address: bool = True
    ) -> SanitizationResult:
        ...
