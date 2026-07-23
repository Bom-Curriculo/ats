"""Builds the prompt used to ask the AI for an ATS quality score of a resume as-is."""

import json

from app.models.resume_analysis import ResumeScoreResult, SkillItem
from app.services.ai.prompt_sources import build_source_sections


def build_resume_score_prompt(
    resume_text: str,
    output_language: str = "pt-BR",
    linkedin_text: str | None = None,
    github_url: str | None = None,
    portfolio_url: str | None = None,
    additional_skills: list[SkillItem] | None = None,
) -> str:
    schema = ResumeScoreResult.model_json_schema()
    instructions = (
        "You are an ATS (Applicant Tracking System) evaluation expert. Read the resume "
        "text below — and the supporting sources after it, if any — and judge how "
        "well-written and ATS-friendly the resume is exactly as given. Do not rewrite, "
        "restructure, or extract the resume — only evaluate it. Produce a 0-100 score "
        "and one direct, actionable improvement suggestion. "
        f"Write the suggestion in {output_language}. "
        f"Return only valid JSON matching this schema: {json.dumps(schema, ensure_ascii=False)}"
    )

    sources = build_source_sections(
        resume_text,
        linkedin_text=linkedin_text,
        github_url=github_url,
        portfolio_url=portfolio_url,
        additional_skills=additional_skills,
    )
    return instructions + "\n\n" + "\n\n".join(sources)
