import logging
import os

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import configurar_logging
from app.providers.base import ErroProvedorIA
from app.schemas.analise import ResultadoAnalise, SolicitacaoAnalise
from app.services.gerenciador_ia import executar_analise_com_fallback

configurar_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bot ATS Resume Builder",
    description="API para análise inicial de currículos compatíveis com ATS.",
    version="0.9.0",
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def verificar_saude() -> dict[str, str]:
    logger.info("health check ok")

    return {"status": "online"}


@app.post("/api/v1/analisar", response_model=ResultadoAnalise)

async def analisar(solicitacao: SolicitacaoAnalise) -> ResultadoAnalise:
    """fall back (recomendação da IA, para os IA hater)"""

    try:
        return await executar_analise_com_fallback(solicitacao)

    except ErroProvedorIA as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
