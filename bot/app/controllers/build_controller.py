from dependency_injector.wiring import Provide, inject
from quart import Blueprint

from app.controllers.resume_input import RequestRejected, resolve_resume_input
from app.core.container import Container
from app.models.error_response import ErrorResponse
from app.providers.base import AIProviderError
from app.services.ai.interfaces import ResumeAnalysisManagerInterface
from app.services.parsing.interfaces import (
    ResumeContentValidatorInterface,
    ResumeFileFetcherInterface,
)

build_blueprint = Blueprint("build", __name__)


@build_blueprint.post("/api/v1/build")
@inject
async def build(
    resume_analysis_manager: ResumeAnalysisManagerInterface = Provide[Container.resume_analysis_manager],
    resume_file_fetcher: ResumeFileFetcherInterface = Provide[Container.resume_file_fetcher],
    resume_content_validator: ResumeContentValidatorInterface = Provide[Container.resume_content_validator],
):
    """Reconstruct the best possible ATS-optimized resume from every given source."""

    try:
        parsed_request, resume_text, linkedin_text = await resolve_resume_input(
            resume_file_fetcher, resume_content_validator
        )
    except RequestRejected as rejection:
        return rejection.body, rejection.status

    try:
        result = await resume_analysis_manager.build_resume(
            resume_text,
            linkedin_text=linkedin_text,
            github_url=parsed_request.github_url,
            portfolio_url=parsed_request.portfolio_url,
            additional_skills=parsed_request.additional_skills,
        )
    except AIProviderError as error:
        return ErrorResponse(detail=str(error)).model_dump(mode="json"), 503

    return result.model_dump(mode="json")
