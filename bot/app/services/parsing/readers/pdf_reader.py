from app.services.parsing.readers.base import MarkItDownReader


class PdfDocumentReader(MarkItDownReader):
    """Extract normalized text from PDF files."""

    extension = ".pdf"
