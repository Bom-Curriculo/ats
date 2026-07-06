from dependency_injector.wiring import Provide, inject
from pydantic import ValidationError
from quart import Blueprint
from quart import request as quart_request

from app.core.container import Container
from app.models.error_response import ErrorResponse
from app.models.resume_analysis import ResumeAnalysisRequest
from app.providers.base import AIProviderError
from app.services.ai.interfaces import ResumeAnalysisManagerInterface

analysis_blueprint = Blueprint("analysis", __name__)


@analysis_blueprint.post("/api/v1/analyze")
@inject
async def analyze(
    resume_analysis_manager: ResumeAnalysisManagerInterface = Provide[Container.resume_analysis_manager],
):
    payload = await quart_request.get_json(force=True, silent=True) or {}
    try:
        analysis_request = ResumeAnalysisRequest.model_validate(payload)
    except ValidationError as error:
        return ErrorResponse(detail=error.errors()).model_dump(mode="json"), 422

    try:
        result = await resume_analysis_manager.extract_resume(analysis_request.resume_text)
    except AIProviderError as error:
        return ErrorResponse(detail=str(error)).model_dump(mode="json"), 503

    return result.model_dump(mode="json")
