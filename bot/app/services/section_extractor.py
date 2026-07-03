
import re
from dataclasses import dataclass, field

from app.services.text_normalizer import normalize_for_comparison, normalize_resume_text

"""bilingue"""
# vatiação de titulos que gepeto deu (chat gpt), pra pt e en
VARIACOES = {
    "resumo_profissional": ("resumo", "resumo profissional", "perfil profissional", "sobre mim", "summary", "professional summary", "profile"),
    "experiencia_profissional": ("experiencia", "experiencia profissional", "historico profissional", "atuacao profissional", "estagios", "estagio", "work experience", "professional experience", "employment history", "internships", "internship experience"),
    "projetos": ("projetos", "projetos de destaque", "projetos pessoais", "portfolio", "projects", "featured projects", "personal projects", "portfolio projects"),
    "projetos_academicos": ("projetos academicos", "projeto academico", "academic projects", "academic project", "university projects"),
    "educacao": ("educacao", "formacao", "formacao academica", "escolaridade", "education", "academic background"),
    "cursos": ("cursos", "cursos complementares", "courses", "training", "professional development"),
    "certificacoes": ("certificacoes", "certificados", "certificacoes e cursos", "cursos e certificacoes", "certifications", "courses and certifications", "licenses", "licenses and certifications"),
    "competencias_tecnicas": ("competencias", "habilidades", "skills", "technical skills", "competencias tecnicas", "tecnologias", "tech stack", "core competencies"),
    "idiomas": ("idiomas", "languages"),
    "conquistas": ("conquistas", "destaques", "premios", "reconhecimentos", "awards", "achievements", "honors"),
    "residencias": ("residencia tecnologica", "residencias tecnologicas", "technology residency", "technical residency"),
    "freelas": ("freelas", "freelance", "freelance work", "trabalhos autonomos", "projetos freelance"),
    "open_source": ("open source", "contribuicoes open source", "open source contributions"),
    "links_portfolio": ("links", "links e portfolio", "contato e links", "contact", "contact and links"),
}


@dataclass
class SectionParserResult:

    secoes: dict[str, str]
    confianca_por_secao: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    secoes_baixa_confianca: list[str] = field(default_factory=list)


def analyze_resume_sections(texto: str) -> SectionParserResult:
    linhas = normalize_resume_text(texto).splitlines()


    # mapa invertido: alias -> chave canônica
    mapa = {alias: chave for chave, aliases in VARIACOES.items() for alias in aliases}
    secoes: dict[str, list[str]] = {"outros": []}
    confianca: dict[str, int] = {}
    atual = "outros"
    headings = 0

    for linha in linhas:
        comparacao = normalize_for_comparison(linha).strip()
        titulo = re.sub(r"[:\-–—]+$", "", comparacao).strip()


        # tenta casar com algum alias conhecido (maior primeiro pra evitar match parcial)
        alias = next((a for a in sorted(mapa, key=len, reverse=True)
                      if titulo == a or comparacao.startswith(a + ":")), None)


        if alias:
            # "Stack:"/"Tecnologias:" inside a project describes that project.
            #
            #
            # não inicia uma seção global de competências
            #
            #
            if atual in {"projetos", "projetos_academicos"} and alias in {"tecnologias", "tech stack"} and ":" in linha:
                secoes[atual].append(linha)
                continue
            atual = mapa[alias]
            headings += 1
            secoes.setdefault(atual, [])
            confianca[atual] = 95 if titulo == alias else 90
            restante = linha.split(":", 1)[1].strip() if ":" in linha else ""
            if restante:
                secoes[atual].append(restante)
            continue
        secoes.setdefault(atual, []).append(linha)

    saida = {k: "\n".join(v).strip() for k, v in secoes.items() if "\n".join(v).strip()}


    warnings, baixas = [], []

    if headings == 0:
        solto = saida.get("outros", "")
        # tenta inferir experiencia por frase introdutoria
        if re.match(r"(?i)^\s*(?:experi[eê]ncia(?:\s+profissional)?|professional\s+experience|experience)\s+(?:com|em|with|in)\b", solto):
            saida = {"experiencia_profissional": solto}
            warnings.append("Experiência inferida por frase introdutória, sem heading explícito.")
            baixas.append("experiencia_profissional")
            confianca["experiencia_profissional"] = 45
        else:
            warnings.append("Nenhum título de seção confiável foi identificado; conteúdo mantido como desconhecido.")
            baixas.append("outros")
            confianca["outros"] = 25
    elif saida.get("outros") and len(saida["outros"]) > 120:
        warnings.append("Há conteúdo relevante fora de seções reconhecidas.")
        baixas.append("outros")
        confianca["outros"] = 35
    return SectionParserResult(saida, confianca, warnings, baixas)


def extract_resume_sections(texto: str) -> dict[str, str]:
    """Contrato legado: retorna somente o mapa de seções."""
    return analyze_resume_sections(texto).secoes


def detect_evidence(texto: str, secoes: dict[str, str]) -> dict[str, bool]:
    normalizado = normalize_for_comparison(texto)
    return {
        "experiencia_profissional": bool(secoes.get("experiencia_profissional")),
        "projetos_pessoais": bool(secoes.get("projetos")),
        "projetos_academicos": bool(secoes.get("projetos_academicos")) or "projeto academico" in normalizado,
        "open_source": bool(secoes.get("open_source")) or bool(re.search(r"\bopen[ -]?source\b", normalizado)),
        "cursos": bool(secoes.get("cursos") or secoes.get("certificacoes")),
        "residencia_tecnologica": bool(secoes.get("residencias")) or "residencia tecnologica" in normalizado,
        "secao_habilidades": bool(secoes.get("competencias_tecnicas")),
    }
