"""Shared source-formatting for the score and resume-construction prompts."""

from app.models.resume_analysis import SkillItem


def build_source_sections(
    resume_text: str,
    linkedin_text: str | None = None,
    github_url: str | None = None,
    portfolio_url: str | None = None,
    additional_skills: list[SkillItem] | None = None,
) -> list[str]:
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
    return sources
