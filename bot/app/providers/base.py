from abc import ABC, abstractmethod

from pydantic import BaseModel


class AIProviderError(RuntimeError):
    """Controlled provider configuration error."""

    def __init__(
        self,
        message: str,
        *,
        category: str = "unknown_provider_error",
        status_http: int | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.status_http = status_http


class AIProvider(ABC):
    """Provider-independent structured-generation interface."""

    name: str
    model: str
    output_language: str = "pt-BR"

    @abstractmethod
    async def run_structured(
        self, prompt: str, schema: type[BaseModel], temperature: float = 0.2
    ) -> BaseModel | None:
        """Ask the model for output matching ``schema`` and return it parsed, or ``None``."""
