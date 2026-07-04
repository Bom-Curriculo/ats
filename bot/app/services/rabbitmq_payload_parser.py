"""Safe parser for RabbitMQ worker input messages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal


class InvalidRabbitMQPayload(ValueError):
    """A message that cannot be processed permanently."""


PayloadFormat = Literal["json", "laravel"]

_ALLOWED_FIELDS = {
    "analysis_request_id",
    "user_id",
    "resume_cv",
    "resume_cv_url",
    "resume_linkedin",
    "resume_linkedin_url",
    "resume_text",
    "job_text",
    "language",
    "job_level",
    "resume_sources",
    "use_ai",
    "curriculo_texto",
    "vaga_texto",
    "expires_link",
    "callback_queue",
}
_URL_RE = re.compile(r"https?://[^\s\"';}]+", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedRabbitMQPayload:
    format: PayloadFormat
    data: dict[str, Any]


def _decode_json(body: bytes | str) -> dict[str, Any]:
    try:
        text = body.decode("utf-8") if isinstance(body, bytes) else body
        value = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise InvalidRabbitMQPayload("mensagem não é um objeto JSON válido") from exc
    if not isinstance(value, dict):
        raise InvalidRabbitMQPayload("mensagem JSON deve ser um objeto")
    return value


def _extract_serialized_value(command: str, field: str) -> str | int | None:
    """Extract simple values without executing or deserializing PHP objects."""
    escaped = re.escape(field)
    # Laravel serializa propriedades protected como "\0*\0campo". O JSON pode
    # Implementation note.
    command = re.sub(
        rf'(?:\x00|\\u0000)(?:\*|[^\x00]*?)(?:\x00|\\u0000){escaped}',
        field,
        command,
        flags=re.IGNORECASE,
    )
    patterns = (
        # Propriedade PHP serializada.
        rf'["\']{escaped}["\']\s*;?\s*'
        rf'(?:s:\d+:)?["\'](?P<string>[^"\']*)["\']',
        rf'["\']{escaped}["\']\s*;?\s*i:(?P<int>\d+)',
        # Implementation note.
        rf'(?<![\w]){escaped}["\']?\s*(?:=>|:|=)\s*["\'](?P<plain>[^"\']*)["\']',
        rf'(?<![\w]){escaped}["\']?\s*(?:=>|:|=)\s*(?P<number>\d+)',
        rf'(?<![\w]){escaped}["\']?\s*(?:=>|:|=)\s*(?P<bare>https?://[^\s;}}]+|[^\s;}}]+)',
    )
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if not match:
            continue
        groups = match.groupdict()
        if groups.get("int") or groups.get("number"):
            return int(groups.get("int") or groups["number"])
        if groups.get("string") is not None:
            return groups["string"]
        return groups.get("plain") if groups.get("plain") is not None else groups.get("bare")
    return None


def _parse_laravel(payload: dict[str, Any]) -> ParsedRabbitMQPayload:
    data = payload.get("data")
    command = data.get("command") if isinstance(data, dict) else None
    if not isinstance(command, str) or "App\\Jobs\\ProcessResumesJobs" not in command:
        raise InvalidRabbitMQPayload("payload Laravel não contém ProcessResumesJobs")

    extracted: dict[str, Any] = {}
    for field in _ALLOWED_FIELDS:
        value = _extract_serialized_value(command, field)
        if value not in (None, ""):
            extracted[field] = value

    urls = _URL_RE.findall(command)
    if urls:
        extracted["urls"] = list(dict.fromkeys(urls))

    # Implementation note.
    if "analysis_request_id" not in extracted and payload.get("uuid"):
        extracted["analysis_request_id"] = str(payload["uuid"])

    return ParsedRabbitMQPayload(format="laravel", data=extracted)


def parse_rabbitmq_payload(body: bytes | str) -> ParsedRabbitMQPayload:
    """Recognize clean JSON or a supported Laravel job."""
    payload = _decode_json(body)
    if isinstance(payload.get("data"), dict) and "command" in payload["data"]:
        return _parse_laravel(payload)

    clean = {key: value for key, value in payload.items() if key in _ALLOWED_FIELDS}
    if not clean:
        raise InvalidRabbitMQPayload("payload JSON não contém campos reconhecidos")
    return ParsedRabbitMQPayload(format="json", data=clean)
