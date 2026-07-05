from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Response body for the ``/health`` endpoint."""

    status: str = "online"

    def to_json(self) -> str:
        return self.model_dump_json()
