import io

from markitdown import MarkItDown

from app.services.parsing.readers.interfaces import DocumentReaderInterface


class MarkItDownReader(DocumentReaderInterface):
    """Shared adapter behavior: delegate extraction and normalization to MarkItDown.

    MarkItDown already normalizes messy PDF/DOCX extraction (headings,
    whitespace, encoding quirks) into clean text, so each format-specific
    subclass only has to declare its file extension.
    """

    extension: str

    def __init__(self, converter: MarkItDown | None = None) -> None:
        self._converter = converter or MarkItDown()

    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(self.extension)

    def read(self, content: bytes) -> str:
        result = self._converter.convert_stream(io.BytesIO(content), file_extension=self.extension)
        return result.text_content.strip()
