from dependency_injector.wiring import Provide, inject
from pydantic import ValidationError
from quart import Blueprint
from quart import request as quart_request

from app.core.container import Container
from app.models.error_response import ErrorResponse
from app.models.resume_analysis import ResumeAnalysisRequest
from app.providers.base import AIProviderError
from app.services.ai.interfaces import ResumeAnalysisManagerInterface
from app.services.parsing.interfaces import (
    ResumeContentValidatorInterface,
    ResumeFileFetcherInterface,
)
from app.services.parsing.resume_file_fetcher import UnfetchableResumeFile

analysis_blueprint = Blueprint("analysis", __name__)


@analysis_blueprint.post("/api/v1/analyze")
@inject
async def analyze(
    resume_analysis_manager: ResumeAnalysisManagerInterface = Provide[Container.resume_analysis_manager],
    resume_file_fetcher: ResumeFileFetcherInterface = Provide[Container.resume_file_fetcher],
    resume_content_validator: ResumeContentValidatorInterface = Provide[Container.resume_content_validator],
):
    payload = await quart_request.get_json(force=True, silent=True) or {}
    try:
        analysis_request = ResumeAnalysisRequest.model_validate(payload)
    except ValidationError as error:
        # include_context=False: pydantic embeds the raw exception object (e.g. our
        # own ValueError from _require_a_cv_source) in each error's `ctx`, which
        # isn't JSON-serializable and would turn this 422 into an unhandled 500.
        return ErrorResponse(detail=error.errors(include_context=False)).model_dump(mode="json"), 422

    try:
        resume_text = await _resolve_text(
            resume_file_fetcher, analysis_request.resume_text, analysis_request.resume_cv_url
        )
        linkedin_text = await _resolve_text(
            resume_file_fetcher, None, analysis_request.resume_linkedin_url
        )
    except UnfetchableResumeFile as error:
        return ErrorResponse(detail=str(error)).model_dump(mode="json"), 422
    except Exception:
        return ErrorResponse(detail="could not download or read one of the file references").model_dump(mode="json"), 422

    # ResumeAnalysisRequest guarantees resume_text or resume_cv_url was given,
    # so this only fires if the URL fetch above returned an empty document.
    if resume_text is None or not resume_text.strip():
        return ErrorResponse(detail="empty").model_dump(mode="json"), 422

    validation = resume_content_validator.validate(resume_text)
    if not validation.is_valid:
        return ErrorResponse(detail=validation.reason).model_dump(mode="json"), 422

    try:
        result = await resume_analysis_manager.extract_resume(
            resume_text,
            linkedin_text=linkedin_text,
            github_url=analysis_request.github_url,
            portfolio_url=analysis_request.portfolio_url,
            additional_skills=analysis_request.additional_skills,
        )
    except AIProviderError as error:
        return ErrorResponse(detail=str(error)).model_dump(mode="json"), 503

    return result.model_dump(mode="json")


async def _resolve_text(
    resume_file_fetcher: ResumeFileFetcherInterface, inline_text: str | None, url: str | None
) -> str | None:
    """Prefer inline text; fall back to downloading and extracting the given URL."""

    if inline_text and inline_text.strip():
        return inline_text
    if not url:
        return None
    return await resume_file_fetcher.fetch_and_extract_text(url)
