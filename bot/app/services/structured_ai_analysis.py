import json
import re
import unicodedata

from app.providers.base import AIProviderError, AIProvider
from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.services.section_extractor import extract_resume_sections
from app.services.privacy_sanitizer import sanitize_personal_data


def _response_json(response: AIAnalysisResponse | dict | str) -> dict:
    if isinstance(response, AIAnalysisResponse):
        return response.model_dump()
    if isinstance(response, dict):
        return response
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    inicio, fim = text.find("{"), text.rfind("}")
    if inicio < 0 or fim <= inicio:
        raise ValueError("Resposta sem objeto JSON")
    carregado = json.loads(text[inicio : fim + 1])
    if not isinstance(carregado, dict):
        raise ValueError("Resposta JSON não é objeto")
    return carregado


def _normalize(text: str) -> str:
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", sem_acentos.casefold()).strip()


def _has_evidence(item: AIRequirementAnalysis, corpus: str) -> bool:
    item_normalizado = _normalize(item.item)
    evidence = _normalize(item.evidence or "")
    return bool(
        (len(item_normalizado) >= 2 and item_normalizado in corpus)
        or (len(evidence) >= 4 and evidence in corpus)
    )


def _is_safe_suggestion(text: str) -> bool:
    normalized = _normalize(text)
    proibidos = (
        "invente ", "finja ", "minta ", "declare experiencia sem", "exagere ",
        "adicione como experiencia mesmo sem", "omita a falta",
    )
    return not any(item in normalized for item in proibidos)


def apply_evidence_gate(
    response: AIAnalysisResponse,
    resume_sanitized: str,
    local_result: AnalysisResult,
) -> AIAnalysisResponse:
    sections = extract_resume_sections(resume_sanitized)
    partes = [resume_sanitized, json.dumps(sections, ensure_ascii=False)]
    partes.append(json.dumps(local_result.resume_inventory or {}, ensure_ascii=False))
    corpus = _normalize("\n".join(partes))
    requirements: list[AIRequirementAnalysis] = []
    gaps = list(response.gaps)

    for requirement in response.contextual_requirements:
        tem_evidence = _has_evidence(requirement, corpus)
        if requirement.status == "found_with_evidence" and not tem_evidence:
            requirement = requirement.model_copy(
                update={
                    "status": "missing",
                    "evidence": None,
                    "rationale": "Não há evidência verificável no currículo sanitizado.",
                    "recommendation": "Trate como lacuna ou confirme antes de incluir no currículo.",
                }
            )
            if requirement.item not in gaps:
                gaps.append(requirement.item)
        elif requirement.evidence and not _has_evidence(requirement, corpus):
            requirement = requirement.model_copy(update={"evidence": None})
        requirements.append(requirement)

    return response.model_copy(
        update={
            "contextual_requirements": requirements,
            "gaps": gaps,
            "improvement_suggestions": [
                s for s in response.improvement_suggestions if _is_safe_suggestion(s)
            ],
            "next_steps": [s for s in response.next_steps if _is_safe_suggestion(s)],
        }
    )


async def run_structured_ai_analysis(
    safe_request: AnalysisRequest,
    local_result: AnalysisResult,
    provider: AIProvider,
) -> AIAnalysisResponse | None:
    """Valida a fronteira externa; falhas viram fallback local controlado."""
    resume = sanitize_personal_data(safe_request.resume_text).text_sanitized
    job = sanitize_personal_data(safe_request.job_text).text_sanitized
    safe = safe_request.model_copy(
        update={"resume_text": resume, "job_text": job}
    )
    try:
        response_raw = await provider.generate_structured_analysis(safe, local_result)
        response = AIAnalysisResponse.model_validate(_response_json(response_raw))
        validada = apply_evidence_gate(response, resume, local_result)
        conteudo_validado = json.dumps(validada.model_dump(), ensure_ascii=False)
        if sanitize_personal_data(conteudo_validado).items_removidos:
            # Implementation note.
            return None
        return validada
    except AIProviderError:
        raise
    except Exception:
        # Implementation note.
        return None
