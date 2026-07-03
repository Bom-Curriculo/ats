import json
import re
import unicodedata

from app.providers.base import AIProviderError, AIProvider
from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.services.section_extractor import extract_resume_sections
from app.services.privacy_sanitizer import sanitize_personal_data


def _json_da_resposta(resposta: AIAnalysisResponse | dict | str) -> dict:
    if isinstance(resposta, AIAnalysisResponse):
        return resposta.model_dump()
    if isinstance(resposta, dict):
        return resposta
    texto = resposta.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.I)
    inicio, fim = texto.find("{"), texto.rfind("}")
    if inicio < 0 or fim <= inicio:
        raise ValueError("Resposta sem objeto JSON")
    carregado = json.loads(texto[inicio : fim + 1])
    if not isinstance(carregado, dict):
        raise ValueError("Resposta JSON não é objeto")
    return carregado


def _normalize(texto: str) -> str:
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", sem_acentos.casefold()).strip()


def _tem_evidencia(item: AIRequirementAnalysis, corpus: str) -> bool:
    item_normalizado = _normalize(item.item)
    evidencia = _normalize(item.evidencia or "")
    return bool(
        (len(item_normalizado) >= 2 and item_normalizado in corpus)
        or (len(evidencia) >= 4 and evidencia in corpus)
    )


def _sugestao_segura(texto: str) -> bool:
    normalizado = _normalize(texto)
    proibidos = (
        "invente ", "finja ", "minta ", "declare experiencia sem", "exagere ",
        "adicione como experiencia mesmo sem", "omita a falta",
    )
    return not any(item in normalizado for item in proibidos)


def apply_evidence_gate(
    resposta: AIAnalysisResponse,
    curriculo_sanitizado: str,
    resultado_local: AnalysisResult,
) -> AIAnalysisResponse:
    secoes = extract_resume_sections(curriculo_sanitizado)
    partes = [curriculo_sanitizado, json.dumps(secoes, ensure_ascii=False)]
    partes.append(json.dumps(resultado_local.inventario_curriculo or {}, ensure_ascii=False))
    corpus = _normalize("\n".join(partes))
    requisitos: list[AIRequirementAnalysis] = []
    lacunas = list(resposta.lacunas)

    for requisito in resposta.requisitos_contextuais:
        tem_evidencia = _tem_evidencia(requisito, corpus)
        if requisito.status == "encontrado_com_evidencia" and not tem_evidencia:
            requisito = requisito.model_copy(
                update={
                    "status": "faltando",
                    "evidencia": None,
                    "justificativa": "Não há evidência verificável no currículo sanitizado.",
                    "recomendacao": "Trate como lacuna ou confirme antes de incluir no currículo.",
                }
            )
            if requisito.item not in lacunas:
                lacunas.append(requisito.item)
        elif requisito.evidencia and not _tem_evidencia(requisito, corpus):
            requisito = requisito.model_copy(update={"evidencia": None})
        requisitos.append(requisito)

    return resposta.model_copy(
        update={
            "requisitos_contextuais": requisitos,
            "lacunas": lacunas,
            "sugestoes_de_melhoria": [
                s for s in resposta.sugestoes_de_melhoria if _sugestao_segura(s)
            ],
            "proximos_passos": [s for s in resposta.proximos_passos if _sugestao_segura(s)],
        }
    )


async def run_structured_ai_analysis(
    solicitacao_segura: AnalysisRequest,
    resultado_local: AnalysisResult,
    provedor: AIProvider,
) -> AIAnalysisResponse | None:
    """Valida a fronteira externa; falhas viram fallback local controlado."""
    curriculo = sanitize_personal_data(solicitacao_segura.resume_text).texto_sanitizado
    vaga = sanitize_personal_data(solicitacao_segura.job_text).texto_sanitizado
    segura = solicitacao_segura.model_copy(
        update={"resume_text": curriculo, "job_text": vaga}
    )
    try:
        resposta_bruta = await provedor.gerar_analise_estruturada(segura, resultado_local)
        resposta = AIAnalysisResponse.model_validate(_json_da_resposta(resposta_bruta))
        validada = apply_evidence_gate(resposta, curriculo, resultado_local)
        conteudo_validado = json.dumps(validada.model_dump(), ensure_ascii=False)
        if sanitize_personal_data(conteudo_validado).itens_removidos:
            # Uma resposta que reintroduz PII ou segredo é rejeitada por inteiro.
            return None
        return validada
    except AIProviderError:
        raise
    except Exception:
        # Nenhum conteúdo externo, prompt ou stack trace é registrado/propagado.
        return None
