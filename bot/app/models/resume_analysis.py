"""Structured resume extraction contract, produced directly from resume text by the AI.

Field names and shapes mirror the Laravel consumer's expected payload exactly
(``analysis_request_id``, ``user_id``, ``result.header/experiences/projects/...``)
so the worker's output can be persisted without any renaming step on the PHP side.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

QualificationType = Literal[
    "elementary_education",
    "high_school",
    "extracurricular_course",
    "technical_course",
    "undergraduate_degree",
    "postgraduate_degree",
    "master_degree",
    "doctorate_degree",
]

LanguageLevel = Literal["beginner", "intermediate", "advanced", "fluent", "native"]


class ResumeHeader(BaseModel):
    name: str | None = None
    headline: str | None = None
    email: str | None = None
    location: str | None = None
    contacts: str | None = None
    emails: str | None = None
    # Keyed by the link's original label as it appears in the resume (e.g. "Portfolio", "GitHub").
    links: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ExperienceItem(BaseModel):
    company: str
    role: str
    # Kept as free-form strings (not `date`): structured-output decoding across
    # providers is far more reliable against a plain string schema than a union type.
    start: str | None = None
    end: str | None = None
    description: str | None = None
    is_actual: bool | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None

    model_config = ConfigDict(extra="forbid")


class ProjectItem(BaseModel):
    title: str
    date: str | None = None
    technologies: str | None = None
    description: str | None = None
    url: str | None = None

    model_config = ConfigDict(extra="forbid")


class QualificationItem(BaseModel):
    type: QualificationType
    institution: str
    title: str
    start: str | None = None
    end: str | None = None
    is_coursing: bool = False

    model_config = ConfigDict(extra="forbid")


class SkillItem(BaseModel):
    name: str
    years: int | None = None

    model_config = ConfigDict(extra="forbid")


class LanguageItem(BaseModel):
    level: LanguageLevel
    language: str

    model_config = ConfigDict(extra="forbid")


class ResumeAnalysisResult(BaseModel):
    """Everything the AI extracts/judges from resume text alone (no job posting involved)."""

    score: int = Field(ge=0, le=100)
    suggestion: str
    header: ResumeHeader = Field(default_factory=ResumeHeader)
    experiences: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    qualifications: list[QualificationItem] = Field(default_factory=list)
    skills: list[SkillItem] = Field(default_factory=list)
    languages: list[LanguageItem] = Field(default_factory=list)
    # Anything else worth keeping that doesn't fit the fields above; stored, never used by the bot itself.
    others: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ResumeAnalysisRequest(BaseModel):
    """HTTP boundary request: resume text only, no job posting to match against."""

    resume_text: str = Field(min_length=1)
