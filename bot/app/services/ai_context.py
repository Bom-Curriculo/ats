from app.schemas.analysis import AnalysisResult, AnalysisRequest
from app.services.privacy_sanitizer import sanitize_personal_data


"""o provider não precisa do payload bruto"""
def _resumir(texto: str, limite: int = 1600) -> str:
    seguro = sanitize_personal_data(texto).texto_sanitizado
    linhas = [linha.strip() for linha in seguro.splitlines() if linha.strip()]
    return "\n".join(linhas)[:limite]


def build_ai_context(solicitacao: AnalysisRequest, resultado: AnalysisResult) -> dict:

    # extrai so oq a ia precisa, td filtrado
    requisitos = [item.model_dump() for item in resultado.analise_por_requisito]
    return {

        "resumo_curriculo_sanitizado": _resumir(solicitacao.resume_text),
        "resumo_vaga_sanitizado": _resumir(solicitacao.job_text),
        "nivel_vaga": resultado.nivel_vaga,
        "titulo_cargo_detectado": ((resultado.avaliacao_relevancia or {}).get("titulo_detectado")),
        "requisitos_extraidos": [r["item"] for r in requisitos],
        "requisitos_por_importancia": requisitos,
        "inventario_relevante": resultado.inventario_curriculo or {},
        "fact_bank": resultado.fact_bank.model_dump() if resultado.fact_bank else None,


        # so manda fonte e nivel, sem expor dado bruto
        "evidencias_por_requisito": [
            {"item": r["item"], "fonte": r["fonte_evidencia"], "nivel": r["nivel_evidencia"]}
            for r in requisitos
        ],
        "lacunas_locais": resultado.palavras_chave_faltando,
        "pontos_fortes_locais": resultado.palavras_chave_encontradas,
        "keyword_report": resultado.keyword_report.model_dump() if resultado.keyword_report else None,
        "alertas_privacidade": ["Conteúdo sanitizado; não reproduzir nem inferir dados pessoais."],


        # regras pra ia não alucinar
        "regras_contra_invencao": [
            "Curso nunca é experiência prática.", "Skill solta nunca é prática.",
            "Projeto é evidência de projeto, não emprego.", "Ausência vira lacuna ou sugestão de estudo/projeto.",
        ],
    }
