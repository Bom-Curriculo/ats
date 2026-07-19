"""Shared HTTP-boundary parsing/validation for the resume-score and resume-build endpoints."""

from pydantic import ValidationError
from quart import request as quart_request

from app.models.error_response import ErrorResponse
from app.models.resume_analysis import ResumeAnalysisRequest
from app.services.parsing.interfaces import (
    ResumeContentValidatorInterface,
    ResumeFileFetcherInterface,
)
from app.services.parsing.resume_file_fetcher import UnfetchableResumeFile


class RequestRejected(Exception):
    """A 4xx the caller should return as-is: ``(body, status)``."""

    def __init__(self, body: dict, status: int) -> None:
        super().__init__(body)
        self.body = body
        self.status = status


async def resolve_resume_input(
    resume_file_fetcher: ResumeFileFetcherInterface,
    resume_content_validator: ResumeContentValidatorInterface,
) -> tuple[ResumeAnalysisRequest, str, str | None]:
    """Parse the request body and resolve resume/LinkedIn text, raising ``RequestRejected`` on any 422."""

    payload = await quart_request.get_json(force=True, silent=True) or {}
    try:
        parsed_request = ResumeAnalysisRequest.model_validate(payload)
    except ValidationError as error:
        # include_context=False: pydantic embeds the raw exception object (e.g. our
        # own ValueError from _require_a_cv_source) in each error's `ctx`, which
        # isn't JSON-serializable and would turn this 422 into an unhandled 500.
        raise RequestRejected(
            ErrorResponse(detail=error.errors(include_context=False)).model_dump(mode="json"), 422
        ) from error

    try:
        resume_text = await _resolve_text(
            resume_file_fetcher, parsed_request.resume_text, parsed_request.resume_cv_url
        )
        linkedin_text = await _resolve_text(
            resume_file_fetcher, None, parsed_request.resume_linkedin_url
        )
    except UnfetchableResumeFile as error:
        raise RequestRejected(ErrorResponse(detail=str(error)).model_dump(mode="json"), 422) from error
    except Exception as error:
        raise RequestRejected(
            ErrorResponse(detail="could not download or read one of the file references").model_dump(mode="json"),
            422,
        ) from error

    # ResumeAnalysisRequest guarantees resume_text or resume_cv_url was given,
    # so this only fires if the URL fetch above returned an empty document.
    if resume_text is None or not resume_text.strip():
        raise RequestRejected(ErrorResponse(detail="empty").model_dump(mode="json"), 422)

    validation = resume_content_validator.validate(resume_text)
    if not validation.is_valid:
        raise RequestRejected(ErrorResponse(detail=validation.reason).model_dump(mode="json"), 422)

    return parsed_request, resume_text, linkedin_text


async def _resolve_text(
    resume_file_fetcher: ResumeFileFetcherInterface, inline_text: str | None, url: str | None
) -> str | None:
    """Prefer inline text; fall back to downloading and extracting the given URL."""

    if inline_text and inline_text.strip():
        return inline_text
    if not url:
        return None
    return await resume_file_fetcher.fetch_and_extract_text(url)
