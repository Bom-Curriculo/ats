from dependency_injector.wiring import Provide, inject
from pydantic import ValidationError
from quart import Blueprint
from quart import request as quart_request

from app.core.container import Container
from app.models.analysis import AnalysisRequest
from app.providers.base import AIProviderError
from app.services.ai.ai_manager import AIManager

analysis_blueprint = Blueprint("analysis", __name__)


async def _run_analysis(ai_manager: AIManager, *, by_alias: bool):
    payload = await quart_request.get_json(force=True, silent=True) or {}
    try:
        analysis_request = AnalysisRequest.model_validate(payload)
    except ValidationError as error:
        return {"detail": error.errors()}, 422

    try:
        result = await ai_manager.run_analysis_with_fallback(analysis_request)
    except AIProviderError as error:
        return {"detail": str(error)}, 503

    return result.model_dump(mode="json", by_alias=by_alias)


@analysis_blueprint.post("/api/v1/analyze")
@inject
async def analyze(ai_manager: AIManager = Provide[Container.ai_manager]):
    return await _run_analysis(ai_manager, by_alias=False)


@analysis_blueprint.post("/api/v1/analisar")
@inject
async def analyze_legacy(ai_manager: AIManager = Provide[Container.ai_manager]):
    """Legacy public API compatibility; remove after client migration."""
    return await _run_analysis(ai_manager, by_alias=True)
