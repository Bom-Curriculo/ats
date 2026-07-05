from pydantic import BaseModel, Field


class SanitizationSummary(BaseModel):
    """Safe-to-return summary of personal data removed before an external AI call."""

    sensitive_data_detected: bool = False
    removed_categories: list[str] = Field(default_factory=list)
    category_count: int = 0
    links_detected_by_type: dict[str, int] = Field(default_factory=dict)
    safe_note: str = ""
