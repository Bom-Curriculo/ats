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
    description="API para análise inicial de currículos compatíveis com ATS.",
    version="0.9.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health_check() -> dict[str, str]:
    logger.info("health check ok")

    return {"status": "online"}


@app.post("/api/v1/analisar", response_model=AnalysisResult)

async def analyze(solicitacao: AnalysisRequest) -> AnalysisResult:
    """fall back (recomendação da IA, para os IA hater)"""

    try:
        return await run_analysis_with_fallback(solicitacao)

    except AIProviderError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
