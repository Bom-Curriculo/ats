from abc import ABC, abstractmethod


class UnsupportedDocumentFormat(ValueError):
    """Raised when no registered reader adapter supports the given file."""


class DocumentReaderInterface(ABC):
    """Extract normalized text from one specific document format."""

    @abstractmethod
    def supports(self, filename: str) -> bool:
        ...

    @abstractmethod
    def read(self, content: bytes) -> str:
        ...


class DocumentReaderAggregatorInterface(ABC):
    """Pick the reader adapter that supports a file and extract its text."""

    @abstractmethod
    def read(self, content: bytes, filename: str) -> str:
        ...
