from pydantic import BaseModel, ConfigDict


class RelevanceEvaluation(BaseModel):
    """Detected job attributes (title, seniority, modality...) used to sanity-check matching."""

    title_detectado: str = ""
    company: str = ""
    area: str = ""
    level: str = ""
    modality: str = ""
    location: str = ""
    accepts_no_experience: bool = False

    # The AI pipeline may return this shape too, with a possibly different field set.
    model_config = ConfigDict(extra="ignore")
