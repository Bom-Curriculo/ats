"""Builds the single prompt used to ask the AI for a full structured resume extraction."""

import json
from datetime import date

from app.models.resume_analysis import ResumeAnalysisResult, SkillItem


def build_resume_extraction_prompt(
    resume_text: str,
    output_language: str = "pt-BR",
    linkedin_text: str | None = None,
    github_url: str | None = None,
    portfolio_url: str | None = None,
    additional_skills: list[SkillItem] | None = None,
) -> str:
    schema = ResumeAnalysisResult.model_json_schema()
    instructions = (
        f"Today's date is {date.today().isoformat()}. "
        "You are an ATS and resume-writing expert. Read the resume text below — and "
        "the supporting sources after it, if any — and extract structured data "
        "faithfully — do not invent, infer, or complete any information that is not "
        "actually present in the given sources. Leave a field null (or an empty list) "
        "when nothing states it. When the LinkedIn text repeats or extends the resume, "
        "merge them into a single coherent set of experiences/qualifications instead of "
        "duplicating entries. Also write a short (2-4 sentence) professional_summary: "
        "an \"about this person\" bio synthesized from the facts actually present in the "
        "given sources (role, seniority, main skills, standout experience) — composing "
        "it is expected even when no source has a literal bio paragraph, but every "
        "claim in it must still be grounded in the given sources, never fabricated. "
        "Also produce a 0-100 score for how well-written and ATS-friendly the resume "
        "is, and one direct, actionable improvement suggestion. "
        f"Write the professional_summary and the suggestion in {output_language}. "
        f"Return only valid JSON matching this schema: {json.dumps(schema, ensure_ascii=False)}"
    )

    sources = [f"Resume text:\n{resume_text}"]
    if linkedin_text:
        sources.append(f"LinkedIn resume text:\n{linkedin_text}")
    if github_url:
        sources.append(
            f"User's GitHub link (add it to header.links under the key \"GitHub\"): {github_url}"
        )
    if portfolio_url:
        sources.append(
            f"User's portfolio link (add it to header.links under the key \"Portfolio\"): {portfolio_url}"
        )
    if additional_skills:
        skills_list = ", ".join(
            f"{skill.name} ({skill.years} anos)" if skill.years is not None else skill.name
            for skill in additional_skills
        )
        sources.append(
            f"Additional skills reported by the user, to merge into the skills list "
            f"(name and years of experience): {skills_list}"
        )

    return instructions + "\n\n" + "\n\n".join(sources)
