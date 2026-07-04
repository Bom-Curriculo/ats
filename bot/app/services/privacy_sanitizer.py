"""Conservative PII, secret, and URL sanitization before external boundaries."""

import re
from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class SanitizationResult:
    text_sanitized: str
    items_removidos: list[str]
    links_detectados_por_type: dict[str, int] = field(default_factory=dict)

    @property
    def sensitive_data_detected(self) -> bool:
        return bool(self.items_removidos)

    @property
    def categories_removidas(self) -> list[str]:
        return self.items_removidos


EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
PHONE = re.compile(r"(?<!\d)(?:\+?55[\s.-]*)?(?:\(\d{2}\)[\s.-]*|\d{2}[\s.-]+)(?:9\d{4}|\d{4})[\s.-]*\d{4}(?!\d)")
CEP = re.compile(r"(?<!\d)\d{5}-?\d{3}(?!\d)")
ADDRESS = re.compile(r"(?im)^\s*(?:endere[cç]o|address)\s*:\s*[^\n]+$")
SECRETS = (
    re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]{16,}|gh[opusr]_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{20,}|(?:api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_.-]{12,})\b"),
    re.compile(r"(?i)\b(?:authorization\s*:\s*(?:bearer\s+)?|bearer\s+)[A-Za-z0-9._~+/-]{8,}={0,2}"),
)
URL = re.compile(r"(?i)\b(?:(?:https?://|www\.)[^\s,;]+|(?:linkedin|github)\.com/[^\s,;]+)")
PORTFOLIO_LINE = re.compile(r"(?im)^(\s*(?:portf[oó]lio|portfolio|website|site pessoal)\s*:\s*)([^\s]+)")
DEPLOY_HOSTS = ("vercel.app", "netlify.app", "github.io", "onrender.com", "railway.app", "pages.dev")


def _classify_url(value: str, portfolio_label: bool = False) -> str:
    limpa = value.rstrip(".)]}>\"'")
    parsed = urlparse(limpa if "://" in limpa else "https://" + limpa)
    host = parsed.netloc.casefold().removeprefix("www.")
    partes = [p for p in parsed.path.split("/") if p]
    if "linkedin.com" in host:
        return "linkedin_url"
    if host == "github.com":
        return "github_repo_url" if len(partes) >= 2 else "github_profile_url"
    if portfolio_label:
        return "portfolio_url"
    if any(host == item or host.endswith("." + item) for item in DEPLOY_HOSTS):
        return "deploy_url"
    return "generic_url"


URL_MARKERS = {
    "linkedin_url": "[LINKEDIN_REMOVIDO]",
    "github_profile_url": "[GITHUB_REMOVIDO]",
    "github_repo_url": "[GITHUB_REMOVIDO]",
    "portfolio_url": "[PORTFOLIO_REMOVIDO]",
    "deploy_url": "[URL_REMOVIDA]",
    "generic_url": "[URL_REMOVIDA]",
}


def sanitize_personal_data(text: str, *, remover_links: bool = True, remover_endereco: bool = True) -> SanitizationResult:
    text_sanitized = text
    found_items: list[str] = []
    links: Counter[str] = Counter()

    def substituir(pattern: re.Pattern[str], marcador: str, category: str) -> None:
        nonlocal text_sanitized
        text_sanitized, quantidade = pattern.subn(marcador, text_sanitized)
        if quantidade and category not in found_items:
            found_items.append(category)

    substituir(EMAIL, "[EMAIL_REMOVIDO]", "email")
    substituir(CPF, "[CPF_REMOVIDO]", "cpf")
    substituir(PHONE, "[TELEFONE_REMOVIDO]", "telefone")
    substituir(CEP, "[CEP_REMOVIDO]", "cep")
    for secret in SECRETS:
        substituir(secret, "[SEGREDO_REMOVIDO]", "secret")
    if remover_endereco:
        substituir(ADDRESS, "[ENDERECO_REMOVIDO]", "endereco")

    if remover_links:
        portfolios: set[str] = set()
        for match in PORTFOLIO_LINE.finditer(text_sanitized):
            portfolios.add(match.group(2).rstrip(".)]}>\"'"))

        def remover_url(match: re.Match[str]) -> str:
            value = match.group(0)
            sufixo = value[len(value.rstrip(".)]}>\"'")):]
            type = _classify_url(value, value.rstrip(".)]}>\"'") in portfolios)
            links[type] += 1
            if type not in found_items:
                found_items.append(type)
            return URL_MARKERS[type] + sufixo

        text_sanitized = URL.sub(remover_url, text_sanitized)

    return SanitizationResult(text_sanitized, found_items, dict(links))
