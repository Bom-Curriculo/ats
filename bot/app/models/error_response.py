from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """HTTP error body for the analysis endpoints."""

    detail: Any

    def to_json(self) -> str:
        return self.model_dump_json()
