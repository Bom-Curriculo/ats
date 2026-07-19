"""Structured resume contracts, produced directly from resume text by the AI.

Two distinct AI outputs share the same input sources (base CV + LinkedIn +
GitHub/portfolio + reported skills): ``ResumeScoreResult`` just judges the
resume as given, while ``BuiltResumeResult`` reconstructs it into the best
possible ATS-optimized version. Field names and shapes mirror the Laravel
consumer's expected payload exactly (``header/experiences/projects/...``) so
the response can be persisted without any renaming step on the PHP side.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    # Kept as free-form strings, same rationale as ExperienceItem.start/end.
    start: str | None = None
    end: str | None = None
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


class ResumeScoreResult(BaseModel):
    """Just an ATS quality judgment of the resume as given — no reconstruction."""

    score: int = Field(ge=0, le=100)
    suggestion: str

    model_config = ConfigDict(extra="forbid")


class BuiltResumeResult(BaseModel):
    """The best possible ATS-optimized version of the resume, reconstructed by the AI

    from the base CV plus every supporting source (no job posting involved).
    """

    score: int = Field(ge=0, le=100)
    # Short first-person-adjacent bio/"about" paragraph, written by the AI from the
    # given sources — not copied verbatim from the resume (most resumes don't have one).
    professional_summary: str | None = None
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
    """HTTP boundary request: the base CV plus optional supporting sources.

    No job posting is involved here. The base CV can arrive as inline text or
    as a URL the bot downloads and extracts itself — exactly one of the two
    is required. Every other source is optional supporting context that gets
    folded into the same extraction instead of triggering a second AI call.
    """

    resume_text: str | None = None
    resume_cv_url: str | None = None
    resume_linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    # Same shape as the output SkillItem (name + years): Laravel sends the skill
    # name and how many years of experience the user reported for it.
    additional_skills: list[SkillItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _require_a_cv_source(self) -> "ResumeAnalysisRequest":
        has_text = bool(self.resume_text and self.resume_text.strip())
        if not has_text and not self.resume_cv_url:
            raise ValueError("either resume_text or resume_cv_url is required")
        return self
