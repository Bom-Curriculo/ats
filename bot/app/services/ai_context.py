from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.services.privacy_sanitizer import sanitize_personal_data


"""Build compact provider context without the raw payload."""
def _summarize(text: str, limite: int = 1600) -> str:
    safe = sanitize_personal_data(text).text_sanitized
    lines = [line.strip() for line in safe.splitlines() if line.strip()]
    return "\n".join(lines)[:limite]


def build_ai_context(request: AnalysisRequest, result: AnalysisResult) -> dict:

    # extrai so oq a ia precisa, td filtrado
    requirements = [item.model_dump() for item in result.requirement_analysis]
    return {

        "summary_resume_sanitized": _summarize(request.resume_text),
        "summary_job_sanitized": _summarize(request.job_text),
        "job_level": result.job_level,
        "title_cargo_detectado": ((result.relevance_evaluation or {}).get("title_detectado")),
        "requirements_extraidos": [r["item"] for r in requirements],
        "requirements_por_importancia": requirements,
        "inventario_relevante": result.resume_inventory or {},
        "fact_bank": result.fact_bank.model_dump() if result.fact_bank else None,


        # Technical note removed during English standardization.
        "evidence_items_por_requirement": [
            {"item": r["item"], "source": r["evidence_source"], "level": r["evidence_level"]}
            for r in requirements
        ],
        "gaps_local": result.missing_keywords,
        "pontos_fortes_local": result.matched_keywords,
        "keyword_report": result.keyword_report.model_dump() if result.keyword_report else None,
        "alerts_privacy": ["Conteúdo sanitizado; não reproduzir nem inferir dados pessoais."],


        # Implementation note.
        "regras_contra_invencao": [
            "Curso nunca é experiência prática.", "Skill solta nunca é prática.",
            "Projeto é evidência de project, não emprego.", "Ausência vira lacuna ou sugestão de estudo/project.",
        ],
    }
