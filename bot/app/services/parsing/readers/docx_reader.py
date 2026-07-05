from app.services.parsing.readers.base import MarkItDownReader


class DocxDocumentReader(MarkItDownReader):
    """Extract normalized text from DOCX files."""

    extension = ".docx"
