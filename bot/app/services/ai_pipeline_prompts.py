
import json

"""Focused prompts that never include the complete fact bank."""

RULES = (
    "Return JSON only. Do not invent facts. A course is not practical experience. "
    "An isolated skill does not prove practice. A project is not employment. Missing data is a gap."
)


def prompt_job_classification(summarized_job: str, local_context: dict, schema: dict) -> str:
    data = {"job": summarized_job[:1800], "local_signals": local_context}
    return f"Classify this job: title, seniority, area, core and secondary requirements, differentials, hard filters, and business context. {RULES} Use exactly this JSON Schema: {json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"


def prompt_contextual_evaluation(classification: dict, requirements: list[dict], evidence_items: list[dict], schema: dict) -> str:
    data = {"classification": classification, "requirements": requirements[:30], "selected_evidence": evidence_items[:20]}
    return f"Evaluate each requirement only from the supplied evidence. Separate real gaps from description gaps and report hallucination risk. {RULES} Use exactly this JSON Schema: {json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"


def prompt_safe_suggestions(evaluations: list[dict], gaps: list[dict], schema: dict) -> str:
    data = {"evaluations": evaluations[:30], "prioritized_gaps": gaps[:20]}
    return f"Generate concise, honest suggestions. Without evidence, recommend study or a real project, never claimed experience. {RULES} Use exactly this JSON Schema: {json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"
