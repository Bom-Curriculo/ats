"""fact bank"""

from collections import Counter
import re

from app.schemas.analise import FactBank
from app.services.catalogo_tecnologias import CATALOGO
from app.services.matching_tecnico import contem_alias
from app.services.parser_entidades_curriculo import bloco_secao, extrair_projetos


# mapeia secao canonica -> (fonte legível, tipo_fonte)
FONTES = {
    "experiencia_profissional": ("experiência profissional", "experiencia_profissional"),
    "projetos": ("projeto", "projeto"),
    "projetos_academicos": ("projeto acadêmico", "projeto_academico"),
    "freelas": ("freela", "freela"), "open_source": ("open source", "open_source"),
    "residencias": ("residência/laboratório prático", "residencia_tecnologica"),
    "cursos": ("curso/formação", "curso_formacao"), "educacao": ("curso/formação", "curso_formacao"),
    "certificacoes": ("certificação", "certificacao"),
    "competencias_tecnicas": ("competências", "competencia"),
    "idiomas": ("idiomas", "idioma"), "conquistas": ("conquista", "conquista"),
}


# extrai só os nomes das tecnologias presentes no texto
def _tecnologias(texto: str) -> list[str]:
    return [t.nome for t in CATALOGO if contem_alias(texto, t.aliases, t.nome)]


def construir_fact_bank(secoes: dict[str, str]) -> FactBank:
    por_fonte: dict[str, list[str]] = {}
    evidencias: list[dict] = []
    for secao, (fonte, tipo) in FONTES.items():
        texto = secoes.get(secao, "").strip()
        if not texto:
            continue
        tecnologias = list(dict.fromkeys(_tecnologias(texto)))
        por_fonte.setdefault(fonte, []).extend(tecnologias)

        # tenta ver se tem entrega real (só pra projeto/freela/open source)
        #
        entrega_real = bool(re.search(
            r"(?i)\b(entreg|cliente|publicad|deploy|contribu|commit|pull request|merged|aceit|implement|desenvolv|delivered|released|built|fixed)\w*\b",
            texto,
        )) if tipo in {"freela", "open_source", "projeto"} else None
        for tecnologia in tecnologias:
            aliases = next(t.aliases for t in CATALOGO if t.nome == tecnologia)
            trecho = next((linha.strip() for linha in texto.splitlines() if contem_alias(linha, aliases, tecnologia)), "")
            evidencias.append({"item": tecnologia, "fonte": fonte, "tipo_fonte": tipo,
                               "evidencia": trecho[:500] or f"Detectado em {fonte}.",
                               "confianca": 90, "entrega_real": entrega_real, "secundaria": False})


    # seção desconhecida (outros) tem peso menor
    #
    desconhecido = secoes.get("outros", "").strip()
    if desconhecido:
        tecnologias = _tecnologias(desconhecido)
        por_fonte["desconhecido"] = tecnologias
        for tecnologia in tecnologias:
            evidencias.append({"item": tecnologia, "fonte": "desconhecido", "tipo_fonte": "desconhecido",
                               "evidencia": "Tecnologia detectada fora de seção confiável.", "confianca": 30,
                               "confianca_baixa": True, "motivo": "Heading de origem não identificado.", "secundaria": False})

    # Marca ocorrências menos fortes como secundárias e mantém tudoi
    #
    #
    #
    ordem = {"experiencia_profissional": 9, "freela": 8, "projeto": 7, "open_source": 6,
             "residencia_tecnologica": 5, "projeto_academico": 4, "curso_formacao": 3,
             "certificacao": 3, "competencia": 2, "idioma": 1, "conquista": 1}


    for item in {x["item"] for x in evidencias}:
        candidatas = [x for x in evidencias if x["item"] == item]

        melhor = max(candidatas, key=lambda x: ordem.get(x["tipo_fonte"], 0))
        for evidencia in candidatas:
            evidencia["secundaria"] = evidencia is not melhor

    projetos = extrair_projetos(secoes.get("projetos", ""), tipo_fonte="projeto")
    academicos = extrair_projetos(secoes.get("projetos_academicos", ""), tipo_fonte="projeto_academico")


    return FactBank(
        experiencias=bloco_secao(secoes.get("experiencia_profissional", ""), "experiencia_profissional"),
        projetos=projetos,
        projetos_academicos=academicos,
        freelas=bloco_secao(secoes.get("freelas", ""), "freela"),
        open_source=bloco_secao(secoes.get("open_source", ""), "open_source"),

        residencias=bloco_secao(secoes.get("residencias", ""), "residencia_tecnologica"),
        cursos=bloco_secao(secoes.get("cursos", ""), "curso_formacao") + bloco_secao(secoes.get("educacao", ""), "curso_formacao"),
        certificacoes=bloco_secao(secoes.get("certificacoes", ""), "certificacao"),
        skills=bloco_secao(secoes.get("competencias_tecnicas", ""), "competencia"),
        idiomas=bloco_secao(secoes.get("idiomas", ""), "idioma"),

        conquistas=bloco_secao(secoes.get("conquistas", ""), "conquista"),
        tecnologias_por_fonte={k: list(dict.fromkeys(v)) for k, v in por_fonte.items()},
        evidencias=evidencias,
    )


# conta quantas evidências por tipo de fonte
def resumo_fontes(fact_bank: FactBank) -> dict[str, int]:
    return dict(Counter(str(x.get("tipo_fonte", "desconhecido")) for x in fact_bank.evidencias))
