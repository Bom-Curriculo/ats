"""Recuperação local limitada de evidências relevantes para a vaga."""

from app.schemas.analise import FactBank, KeywordReport
from app.schemas.pipeline_ia import EvidenciaSelecionada
from app.services.normalizador_texto import normalizar_para_comparacao
from app.services.sanitizador_privacidade import sanitizar_dados_pessoais


FORCA_FONTE = {"experiência profissional": 5, "projeto": 4, "residência/laboratório prático": 3,
               "curso/formação": 2, "competências": 1, "idiomas": 1}


def selecionar_evidencias_relevantes_para_vaga(
    fact_bank: FactBank | None, requisitos: list, keyword_report: KeywordReport | None,
    senioridade: str = "nao_informado", limite: int = 20,
) -> list[EvidenciaSelecionada]:
    if not fact_bank:
        return []

    nomes = [getattr(r, "item", str(r)) for r in requisitos]

    hard_filters = [x.termo for x in keyword_report.hard_filters] if keyword_report else []
    alvos = {normalizar_para_comparacao(x): x for x in nomes + hard_filters}


    candidatas: list[tuple[int, EvidenciaSelecionada]] = []
    for evidencia in fact_bank.evidencias:
        item = str(evidencia.get("item", ""))
        fonte = evidencia.get("fonte")


        relacionados = [original for chave, original in alvos.items() if chave in normalizar_para_comparacao(item) or normalizar_para_comparacao(item) in chave]
        if not relacionados:
            continue
        trecho = sanitizar_dados_pessoais(str(evidencia.get("evidencia", ""))).texto_sanitizado[:500]
        nivel = {"experiência profissional": "pratica_forte", "projeto": "pratica_projeto",
                 "curso/formação": "educacional", "competências": "skill_solta"}.get(fonte, "relacionada")
        bonus = 2 if senioridade in {"pleno", "senior"} and fonte == "experiência profissional" else 0
        score = FORCA_FONTE.get(fonte, 0) + bonus + len(relacionados)


        candidatas.append((score, EvidenciaSelecionada(item=item, fonte=fonte, tipo_fonte=fonte,
            trecho=trecho, nivel_evidencia=nivel, confianca=min(95, 55 + score * 5), relacionado_a=relacionados)))
    candidatas.sort(key=lambda x: (-x[0], x[1].item.casefold()))

    saida, vistos = [], set()

    for _, evidencia in candidatas:

        # Uma tecnologia usa somente sua fonte mais fortee candidatos ficam ordenados []
        chave = evidencia.item.casefold()

        if chave not in vistos:
            vistos.add(chave)
            saida.append(evidencia)

        if len(saida) >= min(limite, 20):
            break
    return saida
