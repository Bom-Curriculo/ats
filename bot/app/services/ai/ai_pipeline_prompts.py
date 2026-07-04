import json

from app.services.ai.interfaces import AIPipelinePromptsInterface

_RULES = (
    "Return JSON only. Do not invent facts. A course is not practical experience. "
    "An isolated skill does not prove practice. A project is not employment. Missing data is a gap."
)


class AIPipelinePrompts(AIPipelinePromptsInterface):
    """Focused prompts that never include the complete fact bank."""

    def job_classification(self, summarized_job: str, local_context: dict, schema: dict) -> str:
        data = {"job": summarized_job[:1800], "local_signals": local_context}
        return (
            "Classify this job: title, seniority, area, core and secondary requirements, "
            f"differentials, hard filters, and business context. {_RULES} Use exactly this "
            f"JSON Schema: {json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"
        )

    def contextual_evaluation(
        self, classification: dict, requirements: list[dict], evidence_items: list[dict], schema: dict
    ) -> str:
        data = {
            "classification": classification,
            "requirements": requirements[:30],
            "selected_evidence": evidence_items[:20],
        }
        return (
            "Evaluate each requirement only from the supplied evidence. Separate real gaps "
            f"from description gaps and report hallucination risk. {_RULES} Use exactly this "
            f"JSON Schema: {json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"
        )

    def safe_suggestions(self, evaluations: list[dict], gaps: list[dict], schema: dict) -> str:
        data = {"evaluations": evaluations[:30], "prioritized_gaps": gaps[:20]}
        return (
            "Generate concise, honest suggestions. Without evidence, recommend study or a "
            f"real project, never claimed experience. {_RULES} Use exactly this JSON Schema: "
            f"{json.dumps(schema, ensure_ascii=False)} Data: {json.dumps(data, ensure_ascii=False)}"
        )
