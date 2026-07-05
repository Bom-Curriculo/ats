from pydantic import BaseModel


class FallbackDetail(BaseModel):
    """Sanitized record of why one AI pipeline step fell back to the local result."""

    step: str
    error_category: str
    safe_message: str
    provider: str
    model: str | None = None
    schema_used: str
