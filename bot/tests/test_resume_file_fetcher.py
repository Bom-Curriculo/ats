import asyncio
from pathlib import Path

import httpx
import pytest

from app.services.parsing.resume_file_fetcher import ResumeFileFetcher, UnfetchableResumeFile

FIXTURES = Path(__file__).parent / "fixtures"


def test_fetch_and_extract_text_downloads_and_reads_docx():
    content = (FIXTURES / "sample_resume.docx").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    fetcher = ResumeFileFetcher(transport=httpx.MockTransport(handler))

    text = asyncio.run(fetcher.fetch_and_extract_text("http://backend:8000/storage/cv.docx"))

    assert "PROFISSIONAL" in text


def test_fetch_and_extract_text_rejects_non_http_scheme():
    fetcher = ResumeFileFetcher()

    with pytest.raises(UnfetchableResumeFile):
        asyncio.run(fetcher.fetch_and_extract_text("file:///etc/passwd"))


def test_fetch_and_extract_text_propagates_http_errors():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    fetcher = ResumeFileFetcher(transport=httpx.MockTransport(handler))

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(fetcher.fetch_and_extract_text("http://backend:8000/storage/missing.docx"))


def test_download_enforces_max_bytes():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 1024)

    fetcher = ResumeFileFetcher(max_bytes=16, transport=httpx.MockTransport(handler))

    with pytest.raises(UnfetchableResumeFile):
        asyncio.run(fetcher.fetch_and_extract_text("http://backend:8000/storage/big.docx"))
