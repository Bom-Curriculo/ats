"""Builds the prompt used to ask the AI to construct the best possible ATS-optimized resume."""

import json
from datetime import date

from app.models.resume_analysis import BuiltResumeResult, SkillItem
from app.services.ai.prompt_sources import build_source_sections


def build_resume_construction_prompt(
    resume_text: str,
    output_language: str = "pt-BR",
    linkedin_text: str | None = None,
    github_url: str | None = None,
    portfolio_url: str | None = None,
    additional_skills: list[SkillItem] | None = None,
) -> str:
    schema = BuiltResumeResult.model_json_schema()
    instructions = (
        f"Today's date is {date.today().isoformat()}. "
        "You are an ATS and resume-writing expert. Read the resume text below — and "
        "the supporting sources after it, if any — and construct the best possible "
        "ATS-optimized version of this person's resume. You may rewrite and strengthen "
        "wording (experience/project descriptions, the professional summary) with clearer "
        "phrasing, action verbs, and better structure — but never invent, infer, or "
        "fabricate a fact (a company, job title, date, technology, institution, or "
        "achievement) that is not actually present in the given sources. When the "
        "LinkedIn text repeats or extends the resume, merge them into a single coherent "
        "set of experiences/qualifications/projects instead of duplicating entries. Every "
        "project must include a start date, and an end date whenever the sources state "
        "one (an open-ended/ongoing project can leave end null). Also write a short (2-4 "
        "sentence) professional_summary: an \"about this person\" bio synthesized from the "
        "facts actually present in the given sources (role, seniority, main skills, "
        "standout experience) — composing it is expected even when no source has a "
        "literal bio paragraph, but every claim in it must still be grounded in the given "
        "sources, never fabricated. Also produce a 0-100 score for how well-written and "
        "ATS-friendly the constructed resume is. "
        f"Write the professional_summary in {output_language}. "
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
