import logging
import os

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_setup import configure_logging
from app.providers.base import AIProviderError
from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.services.ai_manager import run_analysis_with_fallback

configure_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bot ATS Resume Builder",
    description="API for initial ATS-compatible resume analysis.",
    version="0.9.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health_check() -> dict[str, str]:
    logger.info("health check ok")

    return {"status": "online"}


async def _analyze_request(request: AnalysisRequest) -> AnalysisResult:
    """Run the shared analysis flow for both endpoint versions."""

    try:
        return await run_analysis_with_fallback(request)

    except AIProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/api/v1/analyze", response_model=AnalysisResult, response_model_by_alias=False)
async def analyze(request: AnalysisRequest) -> AnalysisResult:
    return await _analyze_request(request)


@app.post("/api/v1/analisar", response_model=AnalysisResult, deprecated=True)
async def analyze_legacy(request: AnalysisRequest) -> AnalysisResult:
    """Legacy public API compatibility; remove after client migration."""
    return await _analyze_request(request)
