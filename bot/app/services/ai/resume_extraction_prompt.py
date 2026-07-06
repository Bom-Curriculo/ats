"""Builds the single prompt used to ask the AI for a full structured resume extraction."""

import json
from datetime import date

from app.models.resume_analysis import ResumeAnalysisResult


def build_resume_extraction_prompt(resume_text: str, output_language: str = "pt-BR") -> str:
    schema = ResumeAnalysisResult.model_json_schema()
    return (
        f"Today's date is {date.today().isoformat()}. "
        "You are an ATS and resume-writing expert. Read the resume text below and "
        "extract its structured data faithfully — do not invent, infer, or complete "
        "any information that is not actually present in the text. Leave a field "
        "null (or an empty list) when the resume does not state it. "
        "Also produce a 0-100 score for how well-written and ATS-friendly the resume "
        "is, and one direct, actionable improvement suggestion. "
        f"Write the suggestion in {output_language}. "
        f"Return only valid JSON matching this schema: {json.dumps(schema, ensure_ascii=False)} "
        f"Resume text:\n{resume_text}"
    )
