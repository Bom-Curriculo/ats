"""Conservative PII, secret, and URL sanitization before external boundaries.

Category names (``email``, ``phone``, ``cpf``, ``cep``, ...) and redaction
markers are part of the response the bot returns; ``cpf`` and ``cep`` are kept
as-is because they name specific Brazilian document/postal formats with no
faithful English equivalent, the same way ``IBAN`` would not be translated.
"""

import re
from collections import Counter
from urllib.parse import urlparse

from app.services.privacy.interfaces import SanitizationResult, SanitizerInterface

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

URL_MARKERS = {
    "linkedin_url": "[LINKEDIN_REMOVED]",
    "github_profile_url": "[GITHUB_REMOVED]",
    "github_repo_url": "[GITHUB_REMOVED]",
    "portfolio_url": "[PORTFOLIO_REMOVED]",
    "deploy_url": "[URL_REMOVED]",
    "generic_url": "[URL_REMOVED]",
}


class PrivacySanitizer(SanitizerInterface):
    """Strip PII, secrets, and sensitive URLs before text crosses an external boundary."""

    def _classify_url(self, value: str, is_portfolio_label: bool = False) -> str:
        cleaned = value.rstrip(".)]}>\"'")
        parsed = urlparse(cleaned if "://" in cleaned else "https://" + cleaned)
        host = parsed.netloc.casefold().removeprefix("www.")
        path_parts = [p for p in parsed.path.split("/") if p]
        if "linkedin.com" in host:
            return "linkedin_url"
        if host == "github.com":
            return "github_repo_url" if len(path_parts) >= 2 else "github_profile_url"
        if is_portfolio_label:
            return "portfolio_url"
        if any(host == item or host.endswith("." + item) for item in DEPLOY_HOSTS):
            return "deploy_url"
        return "generic_url"

    def sanitize(
        self, text: str, *, remove_links: bool = True, remove_address: bool = True
    ) -> SanitizationResult:
        text_sanitized = text
        found_items: list[str] = []
        links: Counter[str] = Counter()

        def replace(pattern: re.Pattern[str], marker: str, category: str) -> None:
            nonlocal text_sanitized
            text_sanitized, count = pattern.subn(marker, text_sanitized)
            if count and category not in found_items:
                found_items.append(category)

        replace(EMAIL, "[EMAIL_REMOVED]", "email")
        replace(CPF, "[CPF_REMOVED]", "cpf")
        replace(PHONE, "[PHONE_REMOVED]", "phone")
        replace(CEP, "[CEP_REMOVED]", "cep")
        for secret in SECRETS:
            replace(secret, "[SECRET_REMOVED]", "secret")
        if remove_address:
            replace(ADDRESS, "[ADDRESS_REMOVED]", "address")

        if remove_links:
            portfolio_urls: set[str] = {
                match.group(2).rstrip(".)]}>\"'") for match in PORTFOLIO_LINE.finditer(text_sanitized)
            }

            def replace_url(match: re.Match[str]) -> str:
                value = match.group(0)
                trimmed = value.rstrip(".)]}>\"'")
                suffix = value[len(trimmed):]
                url_type = self._classify_url(value, trimmed in portfolio_urls)
                links[url_type] += 1
                if url_type not in found_items:
                    found_items.append(url_type)
                return URL_MARKERS[url_type] + suffix

            text_sanitized = URL.sub(replace_url, text_sanitized)

        return SanitizationResult(text_sanitized, found_items, dict(links))
