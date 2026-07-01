import re

from app.services.normalizador_texto import (
    normalizar_para_comparacao,
    normalizar_texto_curriculo,
)

# padrão de lixo q vem dos agregadores de vaga - sla, peguei umas 30 vagas e mandei pro gepeto, oq vale pe a intenção
LINHAS_DESCARTAVEIS = (
    r"\bapply(?:\s+on)?\b",
    r"\bvia\b",
    r"\bindeed\b",
    r"\bglassdoor\b",
    r"\blinkedin\b",
    r"\bgupy\b",
    r"\bsolides\b",
    r"\bquickin\b",
    r"\bbebee\b",
    r"\bjob\s+description\b",
    r"\b\d+\s+days?\s+ago\b",
    r"\bfull[ -]?time\b",
    r"\bstate\s+of\b",
    r"\bc[oó]digo\s+da\s+vaga\b",
)


# regex beneficios
CABECALHO_BENEFICIOS = re.compile(
    r"(?i)^\s*(benef[ií]cios|o que oferecemos|vantagens|perks)\s*:?\s*$"
)


# regex pra seção principal
CABECALHO_RELEVANTE = re.compile(
    r"(?i)^\s*(requisitos|requirements|qualifica[cç][oõ]es|qualifications|responsabilidades|responsibilities|atividades|"
    r"diferenciais|differentials|preferred|nice to have|tecnologias|technologies|stack|sobre a vaga|about the role)\b"
)


def limpar_texto_vaga(texto: str) -> str:
    """remove metadados e beneficios"""

    texto = normalizar_texto_curriculo(texto)

    linhas_limpas: list[str] = []

    ignorando_beneficios = False

    for linha in texto.splitlines():
        if CABECALHO_BENEFICIOS.match(linha):
            ignorando_beneficios = True

            continue

        if ignorando_beneficios and CABECALHO_RELEVANTE.match(linha):
            ignorando_beneficios = False

        if ignorando_beneficios:
            continue

        limpa = linha

        for padrao in LINHAS_DESCARTAVEIS:
            limpa = re.sub(padrao, " ", limpa, flags=re.IGNORECASE)

        limpa = re.sub(r"\s+", " ", limpa).strip(" -|•")

        if limpa:
            linhas_limpas.append(limpa)

    return "\n".join(linhas_limpas)


def normalizar_texto_vaga(texto: str) -> dict[str, str | list[str]]:
    """estrutura a vaga e beneficios e cia não afeta score"""

    campos: dict[str, str | list[str]] = {
        "titulo": "",
        "empresa": "",
        "area": "",
        "localidade": "",
        "modalidade": "",
        "responsabilidades": [],
        "requisitos_obrigatorios": [],
        "diferenciais": [],
        "beneficios": [],
        "informacoes_institucionais": [],
    }

    grupo = "informacoes_institucionais"

    def conteudo_inline(valor: str) -> str:
        if ":" in valor:
            return valor.partition(":")[2].strip()
        partes = valor.split(maxsplit=1)
        return partes[1].strip() if len(partes) == 2 else ""

    for linha_original in normalizar_texto_curriculo(texto).splitlines():
        linha = linha_original

        for padrao in LINHAS_DESCARTAVEIS:
            linha = re.sub(padrao, " ", linha, flags=re.IGNORECASE)

        linha = re.sub(r"\s+", " ", linha).strip(" -|•")

        if not linha:
            continue

        chave = re.sub(r"[^a-z ]", "", normalizar_para_comparacao(linha)).strip()

        if chave.startswith(("responsabilidades", "atividades", "responsibilities")):
            grupo = "responsabilidades"
            linha = conteudo_inline(linha)
            if not linha:
                continue

        if chave.startswith(("requisitos", "requirements", "qualificacoes", "qualifications", "tecnologias", "technologies", "stack")):
            grupo = "requisitos_obrigatorios"
            linha = conteudo_inline(linha)
            if not linha:
                continue

        # Seções funcionais de vagas técnicas representam requisitos centrais.
        if chave in {"front end", "frontend", "back end", "backend", "banco de dados",
                     "devops", "versionamento"}:
            grupo = "requisitos_obrigatorios"
            continue

        if chave.startswith(("diferenciais", "differentials", "desejaveis", "desejveis", "preferred", "nice to have")):
            grupo = "diferenciais"
            linha = conteudo_inline(linha)
            if not linha:
                continue

        if chave.startswith(
            ("benefcios", "beneficios", "o que oferecemos", "vantagens", "perks")
        ):
            grupo = "beneficios"
            continue

        if chave.startswith(("sobre a empresa", "quem somos", "nossa empresa")):
            grupo = "informacoes_institucionais"
            continue

        if not campos["titulo"] and grupo == "informacoes_institucionais":
            campos["titulo"] = linha

        else:
            assert isinstance(campos[grupo], list)

            campos[grupo].append(linha)

    comparacao = normalizar_texto_curriculo(texto)

    modalidade = re.search(r"(?i)\b(remoto|h[ií]brid[oa]|presencial)\b", comparacao)

    campos["modalidade"] = modalidade.group(1) if modalidade else ""

    cidades = (
        "Manaus",
        "Recife",
        "São Paulo",
        "Rio de Janeiro",
        "Belo Horizonte",
        "Curitiba",
        "Porto Alegre",
        "Brasília",
        "Fortaleza",
        "Salvador",
    )

    campos["localidade"] = next(
        (c for c in cidades if c.lower() in comparacao.lower()), ""
    )

    titulo = str(campos["titulo"])
    empresa_rotulada = re.search(r"(?im)^\s*(?:empresa|company)\s*:\s*([^\n]+)", texto)
    campos["empresa"] = empresa_rotulada.group(1).strip() if empresa_rotulada else ""
    corpus = normalizar_para_comparacao(texto)
    areas = (("full stack", ("full stack", "fullstack")), ("front-end", ("front-end", "frontend")),
             ("back-end", ("back-end", "backend")), ("dados", ("dados", "data engineer", "data analyst")),
             ("mobile", ("mobile", "android", "ios")), ("devops", ("devops", "sre")),
             ("qa", ("qa", "quality assurance", "testes")), ("suporte", ("suporte", "support")),
             ("automação", ("automacao", "automation")), ("ia", ("inteligencia artificial", "machine learning", "llm", " rag ")))
    campos["area"] = next((area for area, sinais in areas if any(s in corpus for s in sinais)), "")
    campos["aceita_sem_experiencia"] = bool(re.search(r"(?i)\b(?:sem experiencia|nao exige experiencia|no experience|required experience: none|experience not required)\b", corpus))

    return campos
