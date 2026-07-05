from app.services.parsing.readers.docx_reader import DocxDocumentReader
from app.services.parsing.readers.interfaces import (
    DocumentReaderAggregatorInterface,
    DocumentReaderInterface,
    UnsupportedDocumentFormat,
)
from app.services.parsing.readers.pdf_reader import PdfDocumentReader


class DocumentReaderAggregator(DocumentReaderAggregatorInterface):
    """Dispatch to whichever registered reader adapter supports the file's format."""

    def __init__(self, readers: list[DocumentReaderInterface] | None = None) -> None:
        self._readers = readers or [PdfDocumentReader(), DocxDocumentReader()]

    def read(self, content: bytes, filename: str) -> str:
        reader = next((r for r in self._readers if r.supports(filename)), None)
        if reader is None:
            raise UnsupportedDocumentFormat(f"No reader adapter supports '{filename}'.")
        return reader.read(content)
