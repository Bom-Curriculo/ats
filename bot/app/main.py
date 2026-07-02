from fastapi import FastAPI, HTTPException

from app.providers.base import ErroProvedorIA
from app.schemas.analise import ResultadoAnalise, SolicitacaoAnalise
from app.services.gerenciador_ia import executar_analise_com_fallback

app = FastAPI(
    title="Bot ATS Resume Builder",
    description="API para análise inicial de currículos compatíveis com ATS.",
    version="0.9.0",
)


@app.get("/health")
async def verificar_saude() -> dict[str, str]:

    return {"status": "online"}


@app.post("/api/v1/analisar", response_model=ResultadoAnalise)

async def analisar(solicitacao: SolicitacaoAnalise) -> ResultadoAnalise:
    """fall back (recomendação da IA, para os IA hater)"""

    try:
        return await executar_analise_com_fallback(solicitacao)

    except ErroProvedorIA as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
