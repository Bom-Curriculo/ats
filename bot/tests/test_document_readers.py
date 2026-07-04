from pathlib import Path

import pytest

from app.services.parsing.readers.docx_reader import DocxDocumentReader
from app.services.parsing.readers.interfaces import UnsupportedDocumentFormat
from app.services.parsing.readers.pdf_reader import PdfDocumentReader
from app.services.parsing.readers.reader_aggregator import DocumentReaderAggregator

FIXTURES = Path(__file__).parent / "fixtures"


def test_pdf_reader_supports_only_pdf_extension() -> None:
    reader = PdfDocumentReader()
    assert reader.supports("resume.pdf") is True
    assert reader.supports("RESUME.PDF") is True
    assert reader.supports("resume.docx") is False


def test_docx_reader_supports_only_docx_extension() -> None:
    reader = DocxDocumentReader()
    assert reader.supports("resume.docx") is True
    assert reader.supports("RESUME.DOCX") is True
    assert reader.supports("resume.pdf") is False


def test_pdf_reader_extracts_normalized_text() -> None:
    content = (FIXTURES / "sample_resume.pdf").read_bytes()
    text = PdfDocumentReader().read(content)

    assert "PROFISSIONAL" in text
    assert "FastAPI" in text


def test_docx_reader_extracts_normalized_text() -> None:
    content = (FIXTURES / "sample_resume.docx").read_bytes()
    text = DocxDocumentReader().read(content)

    assert "PROFISSIONAL" in text
    assert "FastAPI" in text


@pytest.mark.parametrize("filename", ["sample_resume.pdf", "sample_resume.docx"])
def test_aggregator_dispatches_to_the_matching_reader(filename: str) -> None:
    content = (FIXTURES / filename).read_bytes()

    text = DocumentReaderAggregator().read(content, filename)

    assert "PROJETOS" in text


def test_aggregator_raises_for_unsupported_format() -> None:
    with pytest.raises(UnsupportedDocumentFormat):
        DocumentReaderAggregator().read(b"plain text", "resume.txt")


def test_aggregator_uses_injected_readers_in_order() -> None:
    calls = []

    class FakeReader:
        def __init__(self, extension: str) -> None:
            self.extension = extension

        def supports(self, filename: str) -> bool:
            return filename.endswith(self.extension)

        def read(self, content: bytes) -> str:
            calls.append(self.extension)
            return f"read via {self.extension}"

    aggregator = DocumentReaderAggregator(readers=[FakeReader(".pdf"), FakeReader(".docx")])

    assert aggregator.read(b"x", "file.docx") == "read via .docx"
    assert calls == [".docx"]
