import re

from app.services.text_normalizer import (
    normalize_for_comparison,
    normalize_resume_text,
)

# Common boilerplate found in job-board descriptions.
DISCARDED_LINES = (
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
BENEFITS_HEADER = re.compile(
    r"(?i)^\s*(benef[ií]cios|o que oferecemos|vantagens|perks)\s*:?\s*$"
)


# Pattern for the main section.
RELEVANT_HEADER = re.compile(
    r"(?i)^\s*(requisitos|requirements|qualifica[cç][oõ]es|qualifications|responsabilidades|responsibilities|atividades|"
    r"diferenciais|differentials|preferred|nice to have|tecnologias|technologies|stack|sobre a vaga|about the role)\b"
)


def clean_job_text(text: str) -> str:
    """remove metadados e beneficios"""

    text = normalize_resume_text(text)

    linhas_limpas: list[str] = []

    ignorando_beneficios = False

    for line in text.splitlines():
        if BENEFITS_HEADER.match(line):
            ignorando_beneficios = True

            continue

        if ignorando_beneficios and RELEVANT_HEADER.match(line):
            ignorando_beneficios = False

        if ignorando_beneficios:
            continue

        limpa = line

        for pattern in DISCARDED_LINES:
            limpa = re.sub(pattern, " ", limpa, flags=re.IGNORECASE)

        limpa = re.sub(r"\s+", " ", limpa).strip(" -|•")

        if limpa:
            linhas_limpas.append(limpa)

    return "\n".join(linhas_limpas)


def normalize_job_text(text: str) -> dict[str, str | list[str]]:
    """Structure job content without allowing benefits to affect scoring."""

    campos: dict[str, str | list[str]] = {
        "title": "",
        "company": "",
        "area": "",
        "localidade": "",
        "modality": "",
        "responsibilities": [],
        "requirements_obrigatorios": [],
        "differentials": [],
        "beneficios": [],
        "informacoes_institucionais": [],
    }

    grupo = "informacoes_institucionais"

    def conteudo_inline(value: str) -> str:
        if ":" in value:
            return value.partition(":")[2].strip()
        partes = value.split(maxsplit=1)
        return partes[1].strip() if len(partes) == 2 else ""

    for original_line in normalize_resume_text(text).splitlines():
        line = original_line

        for pattern in DISCARDED_LINES:
            line = re.sub(pattern, " ", line, flags=re.IGNORECASE)

        line = re.sub(r"\s+", " ", line).strip(" -|•")

        if not line:
            continue

        key = re.sub(r"[^a-z ]", "", normalize_for_comparison(line)).strip()

        if key.startswith(("responsibilities", "atividades", "responsibilities")):
            grupo = "responsibilities"
            line = conteudo_inline(line)
            if not line:
                continue

        if key.startswith(("requisitos", "requirements", "qualificacoes", "qualifications", "technologies", "technologies", "stack")):
            grupo = "requirements_obrigatorios"
            line = conteudo_inline(line)
            if not line:
                continue

        # Technical note removed during English standardization.
        if key in {"front end", "frontend", "back end", "backend", "banco de dados",
                     "devops", "versionamento"}:
            grupo = "requirements_obrigatorios"
            continue

        if key.startswith(("diferenciais", "differentials", "desejaveis", "desejveis", "preferred", "nice to have")):
            grupo = "differentials"
            line = conteudo_inline(line)
            if not line:
                continue

        if key.startswith(
            ("benefcios", "beneficios", "o que oferecemos", "vantagens", "perks")
        ):
            grupo = "beneficios"
            continue

        if key.startswith(("sobre a empresa", "quem somos", "nossa empresa")):
            grupo = "informacoes_institucionais"
            continue

        if not campos["title"] and grupo == "informacoes_institucionais":
            campos["title"] = line

        else:
            assert isinstance(campos[grupo], list)

            campos[grupo].append(line)

    comparison = normalize_resume_text(text)

    modality = re.search(r"(?i)\b(remoto|h[ií]brid[oa]|presencial)\b", comparison)

    campos["modality"] = modality.group(1) if modality else ""

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
        (c for c in cidades if c.lower() in comparison.lower()), ""
    )

    title = str(campos["title"])
    company_rotulada = re.search(r"(?im)^\s*(?:empresa|company)\s*:\s*([^\n]+)", text)
    campos["company"] = company_rotulada.group(1).strip() if company_rotulada else ""
    corpus = normalize_for_comparison(text)
    areas = (("full stack", ("full stack", "fullstack")), ("front-end", ("front-end", "frontend")),
             ("back-end", ("back-end", "backend")), ("data", ("data", "data engineer", "data analyst")),
             ("mobile", ("mobile", "android", "ios")), ("devops", ("devops", "sre")),
             ("qa", ("qa", "quality assurance", "testes")), ("suporte", ("suporte", "support")),
             ("automação", ("automacao", "automation")), ("ia", ("inteligencia artificial", "machine learning", "llm", " rag ")))
    campos["area"] = next((area for area, sinais in areas if any(s in corpus for s in sinais)), "")
    campos["accepts_no_experience"] = bool(re.search(r"(?i)\b(?:sem experiencia|nao exige experiencia|no experience|required experience: none|experience not required)\b", corpus))

    return campos
