"""Application configuration.

Non-secret values are read from ``config.yaml``. Secrets (API keys, RabbitMQ
credentials) are read only from the environment / ``.env`` and are never
written to the YAML file. A handful of legacy environment variables
(``IA_PROVIDER``, ``RABBITMQ_HOST``, ...) still override their ``config.yaml``
counterpart, preserving current deployment behavior.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

_PROVIDER_KEY_ENV_VARS = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
}


@dataclass(frozen=True)
class ProviderSettings:
    model: str
    timeout_seconds: float
    api_key: str = ""
    base_url: str | None = None

    def is_configured(self) -> bool:
        if self.base_url is not None:
            return bool(self.base_url.strip() and self.model.strip())
        return bool(self.api_key.strip())


@dataclass(frozen=True)
class AISettings:
    enabled_by_default: bool
    output_language: str
    provider: str
    provider_chain: tuple[str, ...]
    providers: dict[str, ProviderSettings] = field(default_factory=dict)


@dataclass(frozen=True)
class RabbitMQSettings:
    host: str
    port: int
    vhost: str
    user: str
    password: str
    input_queue: str
    output_queue: str
    heartbeat_seconds: int
    blocked_connection_timeout_seconds: int


@dataclass(frozen=True)
class ServerSettings:
    host: str
    port: int
    log_level: str


@dataclass(frozen=True)
class Settings:
    server: ServerSettings
    ai: AISettings
    rabbitmq: RabbitMQSettings

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Settings":
        path = config_path or (PROJECT_ROOT / "config.yaml")
        raw: dict = yaml.safe_load(path.read_text()) if path.exists() else {}

        server_raw = raw.get("server") or {}
        ai_raw = raw.get("ai") or {}
        rabbitmq_raw = raw.get("rabbitmq") or {}

        return cls(
            server=cls._build_server_settings(server_raw),
            ai=cls._build_ai_settings(ai_raw),
            rabbitmq=cls._build_rabbitmq_settings(rabbitmq_raw),
        )

    @staticmethod
    def _build_server_settings(raw: dict) -> ServerSettings:
        return ServerSettings(
            host=raw.get("host", "0.0.0.0"),
            port=int(raw.get("port", 8000)),
            log_level=os.getenv("LOG_LEVEL", raw.get("log_level", "INFO")),
        )

    @staticmethod
    def _build_ai_settings(raw: dict) -> AISettings:
        providers = {
            name: ProviderSettings(
                model=provider_raw["model"],
                timeout_seconds=float(provider_raw.get("timeout_seconds", 120.0)),
                api_key=os.getenv(_PROVIDER_KEY_ENV_VARS.get(name, ""), ""),
                base_url=provider_raw.get("base_url"),
            )
            for name, provider_raw in (raw.get("providers") or {}).items()
        }
        default_chain = ",".join(raw.get("provider_chain") or [])
        chain = tuple(
            item.strip().lower()
            for item in os.getenv("IA_PROVIDER_CHAIN", default_chain).split(",")
            if item.strip()
        )
        return AISettings(
            enabled_by_default=_env_flag("USAR_IA_PADRAO", raw.get("enabled_by_default", True)),
            output_language=raw.get("output_language", "pt-BR"),
            provider=os.getenv("IA_PROVIDER", raw.get("provider", "auto")).strip().lower(),
            provider_chain=chain,
            providers=providers,
        )

    @staticmethod
    def _build_rabbitmq_settings(raw: dict) -> RabbitMQSettings:
        return RabbitMQSettings(
            host=os.getenv("RABBITMQ_HOST", raw.get("host", "rabbitmq")),
            port=int(os.getenv("RABBITMQ_PORT", raw.get("port", 5672))),
            vhost=os.getenv("RABBITMQ_VHOST", raw.get("vhost", "/")),
            user=os.getenv("RABBITMQ_USER", "bomcurriculo"),
            password=os.getenv("RABBITMQ_PASSWORD", "bomcurriculo"),
            input_queue=os.getenv("RABBITMQ_INPUT_QUEUE", raw.get("input_queue", "resumes_laravel_queue")),
            output_queue=os.getenv(
                "RABBITMQ_OUTPUT_QUEUE", raw.get("output_queue", "resumes_output")
            ),
            heartbeat_seconds=int(raw.get("heartbeat_seconds", 60)),
            blocked_connection_timeout_seconds=int(
                raw.get("blocked_connection_timeout_seconds", 30)
            ),
        )


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "nao", "não", "off"}
