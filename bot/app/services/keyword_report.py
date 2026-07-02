import re

from app.schemas.analise import ItemAnaliseRequisito, ItemKeyword, KeywordReport
from app.services.normalizador_texto import normalizar_para_comparacao


PESOS = {"hard_skills": 2.0, "title_function_keywords": 1.5, "business_context": 1.0,
         "action_keywords": 1.0, "domain_keywords": 1.0}


def _hard_filters(vaga: str, curriculo: str) -> tuple[list[ItemKeyword], list[str]]:
    filtros: list[ItemKeyword] = []

    alertas: list[str] = []
    vaga_n, cv_n = normalizar_para_comparacao(vaga), normalizar_para_comparacao(curriculo)
    padroes = [r"\b\d+\+?\s*anos?\b", r"graduacao completa", r"ingles avancado",
               r"\b(?:presencial|hibrid[oa])\b"]

    for padrao in padroes:
        for match in re.finditer(padrao, vaga_n):
            termo = match.group(0)
            presente = termo in cv_n

            filtros.append(ItemKeyword(termo=termo, categoria="hard_filters", peso=0, presente=presente))
            if not presente:
                alertas.append(f"Possível impeditivo: hard filter não comprovado no currículo: {termo}.")

    return filtros, list(dict.fromkeys(alertas))


def construir_keyword_report(itens: list[ItemAnaliseRequisito], vaga: str, curriculo: str, titulo: str = "") -> tuple[KeywordReport, int, list[ItemKeyword], list[ItemKeyword]]:
    grupos: dict[str, list[ItemKeyword]] = {k: [] for k in PESOS}
    titulo_n = normalizar_para_comparacao(titulo)


    for item in itens:
        if item.tipo == "tecnologia":
            categoria = "hard_skills"

        elif normalizar_para_comparacao(item.item) in titulo_n and titulo_n:
            categoria = "title_function_keywords"

        elif item.categoria == "responsabilidade":
            categoria = "action_keywords"

        elif item.categoria == "contexto":
            categoria = "business_context"

        else:
            categoria = "domain_keywords"
        presente = item.status in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro"}
        grupos[categoria].append(ItemKeyword(termo=item.item, categoria=categoria, peso=PESOS[categoria], presente=presente, fonte=item.fonte_evidencia))
    filtros, alertas = _hard_filters(vaga, curriculo)
    todos = [kw for valores in grupos.values() for kw in valores]


    # não separa em vários requisitros e o o peso fica baixo
    sql_nomes = {"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}
    sql = [kw for kw in todos if kw.termo in sql_nomes]
    pontuaveis = [kw for kw in todos if kw.termo not in sql_nomes]
    total = sum(kw.peso for kw in pontuaveis)
    obtido = sum(kw.peso for kw in pontuaveis if kw.presente)
    if sql:
        peso_sql = max(kw.peso for kw in sql)
        total += peso_sql
        if any(kw.presente for kw in sql):
            obtido += peso_sql
    score = round(obtido / total * 100) if total else 0
    report = KeywordReport(**grupos, hard_filters=filtros, alertas_hard_filters=alertas)
    return report, score, [x for x in todos if x.presente], [x for x in todos if not x.presente]
