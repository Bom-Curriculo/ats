"""Sanitização conservadora de PII, segredos e URLs antes de fronteiras externas."""

import re
from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class SanitizationResult:
    texto_sanitizado: str
    itens_removidos: list[str]
    links_detectados_por_tipo: dict[str, int] = field(default_factory=dict)

    @property
    def dados_sensiveis_detectados(self) -> bool:
        return bool(self.itens_removidos)

    @property
    def categorias_removidas(self) -> list[str]:
        return self.itens_removidos


EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
TELEFONE = re.compile(r"(?<!\d)(?:\+?55[\s.-]*)?(?:\(\d{2}\)[\s.-]*|\d{2}[\s.-]+)(?:9\d{4}|\d{4})[\s.-]*\d{4}(?!\d)")
CEP = re.compile(r"(?<!\d)\d{5}-?\d{3}(?!\d)")
ENDERECO = re.compile(r"(?im)^\s*(?:endere[cç]o|address)\s*:\s*[^\n]+$")
SEGREDOS = (
    re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]{16,}|gh[opusr]_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{20,}|(?:api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_.-]{12,})\b"),
    re.compile(r"(?i)\b(?:authorization\s*:\s*(?:bearer\s+)?|bearer\s+)[A-Za-z0-9._~+/-]{8,}={0,2}"),
)
URL = re.compile(r"(?i)\b(?:(?:https?://|www\.)[^\s,;]+|(?:linkedin|github)\.com/[^\s,;]+)")
PORTFOLIO_LINHA = re.compile(r"(?im)^(\s*(?:portf[oó]lio|portfolio|website|site pessoal)\s*:\s*)([^\s]+)")
DEPLOY_HOSTS = ("vercel.app", "netlify.app", "github.io", "onrender.com", "railway.app", "pages.dev")


def _classify_url(valor: str, rotulo_portfolio: bool = False) -> str:
    limpa = valor.rstrip(".)]}>\"'")
    parsed = urlparse(limpa if "://" in limpa else "https://" + limpa)
    host = parsed.netloc.casefold().removeprefix("www.")
    partes = [p for p in parsed.path.split("/") if p]
    if "linkedin.com" in host:
        return "linkedin_url"
    if host == "github.com":
        return "github_repo_url" if len(partes) >= 2 else "github_profile_url"
    if rotulo_portfolio:
        return "portfolio_url"
    if any(host == item or host.endswith("." + item) for item in DEPLOY_HOSTS):
        return "deploy_url"
    return "generic_url"


MARCADORES_URL = {
    "linkedin_url": "[LINKEDIN_REMOVIDO]",
    "github_profile_url": "[GITHUB_REMOVIDO]",
    "github_repo_url": "[GITHUB_REMOVIDO]",
    "portfolio_url": "[PORTFOLIO_REMOVIDO]",
    "deploy_url": "[URL_REMOVIDA]",
    "generic_url": "[URL_REMOVIDA]",
}


def sanitize_personal_data(texto: str, *, remover_links: bool = True, remover_endereco: bool = True) -> SanitizationResult:
    texto_sanitizado = texto
    encontrados: list[str] = []
    links: Counter[str] = Counter()

    def substituir(padrao: re.Pattern[str], marcador: str, categoria: str) -> None:
        nonlocal texto_sanitizado
        texto_sanitizado, quantidade = padrao.subn(marcador, texto_sanitizado)
        if quantidade and categoria not in encontrados:
            encontrados.append(categoria)

    substituir(EMAIL, "[EMAIL_REMOVIDO]", "email")
    substituir(CPF, "[CPF_REMOVIDO]", "cpf")
    substituir(TELEFONE, "[TELEFONE_REMOVIDO]", "telefone")
    substituir(CEP, "[CEP_REMOVIDO]", "cep")
    for segredo in SEGREDOS:
        substituir(segredo, "[SEGREDO_REMOVIDO]", "segredo")
    if remover_endereco:
        substituir(ENDERECO, "[ENDERECO_REMOVIDO]", "endereco")

    if remover_links:
        portfolios: set[str] = set()
        for match in PORTFOLIO_LINHA.finditer(texto_sanitizado):
            portfolios.add(match.group(2).rstrip(".)]}>\"'"))

        def remover_url(match: re.Match[str]) -> str:
            valor = match.group(0)
            sufixo = valor[len(valor.rstrip(".)]}>\"'")):]
            tipo = _classify_url(valor, valor.rstrip(".)]}>\"'") in portfolios)
            links[tipo] += 1
            if tipo not in encontrados:
                encontrados.append(tipo)
            return MARCADORES_URL[tipo] + sufixo

        texto_sanitizado = URL.sub(remover_url, texto_sanitizado)

    return SanitizationResult(texto_sanitizado, encontrados, dict(links))
