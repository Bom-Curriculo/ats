import json
from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from app.models.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.models.ai_analysis import AIAnalysisResponse
from app.services.ai.ai_context import AIContextBuilder
from app.services.privacy.interfaces import SanitizerInterface


class AIProviderError(RuntimeError):
    """Controlled provider configuration error."""

    def __init__(
        self,
        message: str,
        *,
        category: str = "unknown_provider_error",
        status_http: int | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.status_http = status_http


class AIProvider(ABC):
    """Provider-independent interface."""

    name: str
    model: str
    output_language: str = "pt-BR"

    @abstractmethod
    async def generate_completion(
        self,
        request: AnalysisRequest,
        base_result: AnalysisResult,
    ) -> AIComplement:
        """Return a minimal AI complement (summary + suggestions) for the request."""

    async def generate_structured_analysis(
        self, safe_request: AnalysisRequest, local_result: AnalysisResult
    ) -> AIAnalysisResponse | dict | str:
        complement = await self.generate_completion(safe_request, local_result)
        return AIAnalysisResponse(
            contextual_summary=complement.generated_summary,
            contextual_requirements=[],
            strengths=[],
            gaps=[],
            possible_blockers=[],
            improvement_suggestions=complement.suggestions,
            next_steps=[],
            anti_fabrication_alerts=[],
            confidence=50,
        )

    async def run_structured_task(
        self, task: str, prompt: str, schema: type, temperature: float = 0.1
    ) -> dict[str, Any] | None:
        return None


def create_prompt(
    request: AnalysisRequest,
    base_result: AnalysisResult,
    output_language: str = "pt-BR",
    sanitizer: SanitizerInterface | None = None,
) -> str:
    """Build one instruction and require a compact, predictable JSON response."""

    data = AIContextBuilder().build(request, base_result, sanitizer)
    schema = AIAnalysisResponse.model_json_schema()
    return (
        f"Today's date is {date.today().isoformat()}. "
        "You are an ATS and recruitment resume expert. Analyze the sanitized resume "
        "against the sanitized job description. Return only valid JSON in the requested "
        "schema. Do not use Markdown. Do not invent experience, technology, course, "
        "company, role, education, language, city, availability, certification, metric, "
        "or project. If something does not appear in the resume, classify it as a gap. "
        "Partial evidence is related_but_not_explicit; a term without enough context is "
        "found_without_clear_context. "
        "Do not reintroduce phone numbers, email, national ID, address, LinkedIn, or GitHub. "
        "Do not claim as experience an absent technology; treat it as a gap. "
        "Do not confuse Docker with Kubernetes, ChatGPT web with AI APIs, or GitHub with "
        "branch/pull-request/code-review workflows. "
        "Separate a real gap from a missing description. Suggest study or a project when "
        "there is no evidence. Related evidence is not a direct match. Open source is a "
        "differential, not a requirement. A course is educational evidence, never "
        "professional experience. For internship/junior roles, courses and projects carry "
        "relevant weight and lacking professional experience does not automatically fail "
        "the candidate. For mid/senior roles, a course without practical application carries "
        "low weight, and real experience, production impact, and collaboration weigh more. "
        "Frameworks can imply languages (Spring Boot/Java, FastAPI/Python, Laravel/PHP, "
        "Next.js/React), but that does not imply practical experience. Do not mark HTML5 as "
        "missing if HTML is present, nor CSS3 as missing if CSS is present. Do not mark REST "
        "APIs as missing if REST API appears in a project, summary, or skills. Spring Boot "
        "mentioned only in a course is found_without_clear_context, not "
        "found_with_evidence. When in doubt, use related_but_not_explicit. Experience can be "
        "partially compensated by personal or academic projects, practical courses, tech "
        "residencies, labs, and a portfolio. A technical skills section is strongly "
        "recommended for tech ATS but its absence does not automatically fail the candidate. "
        "Distinguish immediate adjustments, technical gaps, possible blockers, and next "
        "steps. Be specific, direct, honest, and write in "
        f"{output_language}. Do not ask the user to lie. Do not reproduce personal data. "
        f"Schema: {json.dumps(schema, ensure_ascii=False)} "
        f"Safe data:\n{json.dumps(data, ensure_ascii=False)}"
    )
