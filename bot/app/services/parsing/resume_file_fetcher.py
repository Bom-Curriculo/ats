"""Downloads a resume/LinkedIn file reference and extracts its text.

Only handles fields that are already absolute ``http(s)`` URLs (the PHP
backend's own storage/R2 links) — the worker never guesses a base host for a
bare relative path such as ``uploads/resumes/cvs/foo.docx``.
"""

from __future__ import annotations

import httpx

from app.services.parsing.interfaces import ResumeFileFetcherInterface
from app.services.parsing.readers.interfaces import DocumentReaderAggregatorInterface
from app.services.parsing.readers.reader_aggregator import DocumentReaderAggregator

_ALLOWED_SCHEMES = ("http://", "https://")
DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB


class UnfetchableResumeFile(ValueError):
    """A file reference that cannot or should not be downloaded."""


class ResumeFileFetcher(ResumeFileFetcherInterface):
    def __init__(
        self,
        reader_aggregator: DocumentReaderAggregatorInterface | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = DEFAULT_MAX_BYTES,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._reader_aggregator = reader_aggregator or DocumentReaderAggregator()
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._transport = transport

    async def fetch_and_extract_text(self, url: str) -> str:
        if not url.lower().startswith(_ALLOWED_SCHEMES):
            raise UnfetchableResumeFile("unsupported URL scheme")

        content = await self._download(url)
        filename = httpx.URL(url).path.rsplit("/", 1)[-1] or "resume"
        return self._reader_aggregator.read(content, filename)

    async def _download(self, url: str) -> bytes:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds, follow_redirects=True, transport=self._transport
        ) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > self._max_bytes:
                        raise UnfetchableResumeFile("file exceeds the maximum allowed size")
                return bytes(body)
