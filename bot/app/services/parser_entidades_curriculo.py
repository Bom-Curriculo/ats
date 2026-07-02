"""isso é dentro de seções já classificadas"""

import re

from app.services.catalogo_tecnologias import CATALOGO
from app.services.matching_tecnico import contem_alias


PREFIXOS_STACK = re.compile(r"(?i)^\s*(?:tecnologias?|technology|technologies|stack|tech stack)\s*:\s*(.+)$")
BULLET = re.compile(r"^\s*[-•*]\s*")


def tecnologias_no_texto(texto: str) -> list[str]:
    return [t.nome for t in CATALOGO if contem_alias(texto, t.aliases, t.nome)]


def _parece_titulo(linha: str, proxima: str = "") -> bool:
    limpa = BULLET.sub("", linha).strip()
    if not limpa or PREFIXOS_STACK.match(limpa) or len(limpa) > 90 or len(limpa.split()) > 12:
        return False

    if re.search(r"[.!?]$", limpa) or re.match(r"(?i)^(desenvolv|implement|criad|respons|utiliz|built|developed|implemented)\b", limpa):
        return False
    return bool(PREFIXOS_STACK.match(proxima) or " | " in limpa or re.match(r"(?i)^(projeto|project)\s+", limpa))


def extrair_projetos(texto: str, *, tipo_fonte: str = "projeto") -> list[dict]:
    linhas = [x.strip() for x in texto.splitlines() if x.strip()]
    if not linhas:
        return []

    inicios = [i for i, linha in enumerate(linhas)
               if _parece_titulo(linha, linhas[i + 1] if i + 1 < len(linhas) else "")]
    if not inicios:
        return [{"nome": None, "tecnologias": tecnologias_no_texto(texto), "descricao": texto[:2000],
                 "evidencias_entrega": [x for x in linhas if BULLET.match(x)][:12],
                 "fonte": tipo_fonte, "confianca": 45, "confianca_baixa": True,
                 "motivo": "Seção de projetos sem delimitadores claros."}]


    projetos = []
    for pos, inicio in enumerate(inicios):


        fim = inicios[pos + 1] if pos + 1 < len(inicios) else len(linhas)
        bloco = linhas[inicio:fim]
        nome = BULLET.sub("", bloco[0]).strip()
        stack_explica = [PREFIXOS_STACK.match(x).group(1) for x in bloco[1:] if PREFIXOS_STACK.match(x)]
        descricao_linhas = [x for x in bloco[1:] if not PREFIXOS_STACK.match(x)]

        descricao = "\n".join(descricao_linhas)
        entregas = [BULLET.sub("", x).strip() for x in descricao_linhas
                    if BULLET.match(x) or re.search(r"(?i)\b(entreg|publicad|deploy|implement|desenvolv|automat|integ|built|released|delivered|implemented)\w*\b", x)]
        corpus = " ".join(bloco + stack_explica)

        projetos.append({"nome": nome, "tecnologias": tecnologias_no_texto(corpus),
                         "descricao": descricao[:2000], "evidencias_entrega": entregas[:12],
                         "fonte": tipo_fonte, "confianca": 90 if stack_explica else 75,
                         "confianca_baixa": False, "motivo": None})


    return projetos


def bloco_secao(texto: str, fonte: str, confianca: int = 90) -> list[dict]:
    if not texto.strip():
        return []

    return [{"conteudo": texto.strip()[:5000], "fonte": fonte, "confianca": confianca,
             "confianca_baixa": confianca < 60, "motivo": None if confianca >= 60 else "Fonte inferida sem heading confiável."}]
