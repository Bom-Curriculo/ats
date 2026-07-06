from typing import Any

from pydantic import BaseModel, Field


class RabbitMQOutputMessage(BaseModel):
    """Message body published back to the RabbitMQ output/callback queue."""

    analysis_request_id: Any = None
    user_id: Any = None
    status: str
    source: str = "bot-python"
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None

    def to_json_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")
