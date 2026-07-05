from abc import ABC, abstractmethod

from app.providers.base import AIProvider


class ProviderFactoryInterface(ABC):
    """Builds configured `AIProvider` instances from settings alone."""

    @abstractmethod
    def is_configured(self, name: str) -> bool:
        ...

    @abstractmethod
    def create(self, name: str | None = None) -> AIProvider:
        ...
