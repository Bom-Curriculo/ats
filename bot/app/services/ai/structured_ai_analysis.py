import json
import re
import unicodedata

from app.providers.base import AIProviderError, AIProvider
from app.models.analysis import AnalysisResult, AnalysisRequest
from app.models.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.services.ai.interfaces import StructuredAIAnalysisValidatorInterface
from app.services.parsing.section_extractor import extract_resume_sections
from app.services.privacy.interfaces import SanitizerInterface
from app.services.privacy.sanitizer import PrivacySanitizer

_FORBIDDEN_SUGGESTION_PHRASES = (
    "invente ", "finja ", "minta ", "declare experiencia sem", "exagere ",
    "adicione como experiencia mesmo sem", "omita a falta",
)


def _response_json(response: AIAnalysisResponse | dict | str) -> dict:
    if isinstance(response, AIAnalysisResponse):
        return response.model_dump()
    if isinstance(response, dict):
        return response
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Response has no JSON object")
    loaded = json.loads(text[start : end + 1])
    if not isinstance(loaded, dict):
        raise ValueError("JSON response is not an object")
    return loaded


def _normalize(text: str) -> str:
    without_accents = "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", without_accents.casefold()).strip()


class StructuredAIAnalysisValidator(StructuredAIAnalysisValidatorInterface):
    """Validate the external AI boundary; failures become a controlled local fallback."""

    def _has_evidence(self, item: AIRequirementAnalysis, corpus: str) -> bool:
        normalized_item = _normalize(item.item)
        normalized_evidence = _normalize(item.evidence or "")
        return bool(
            (len(normalized_item) >= 2 and normalized_item in corpus)
            or (len(normalized_evidence) >= 4 and normalized_evidence in corpus)
        )

    def _is_safe_suggestion(self, text: str) -> bool:
        normalized = _normalize(text)
        return not any(phrase in normalized for phrase in _FORBIDDEN_SUGGESTION_PHRASES)

    def apply_evidence_gate(
        self,
        response: AIAnalysisResponse,
        resume_sanitized: str,
        local_result: AnalysisResult,
    ) -> AIAnalysisResponse:
        sections = extract_resume_sections(resume_sanitized)
        parts = [resume_sanitized, json.dumps(sections, ensure_ascii=False)]
        parts.append(json.dumps(local_result.resume_inventory or {}, ensure_ascii=False))
        corpus = _normalize("\n".join(parts))
        requirements: list[AIRequirementAnalysis] = []
        gaps = list(response.gaps)

        for requirement in response.contextual_requirements:
            has_evidence = self._has_evidence(requirement, corpus)
            if requirement.status == "found_with_evidence" and not has_evidence:
                requirement = requirement.model_copy(
                    update={
                        "status": "missing",
                        "evidence": None,
                        "rationale": "Não há evidência verificável no currículo sanitizado.",
                        "recommendation": "Trate como lacuna ou confirme antes de incluir no currículo.",
                    }
                )
                if requirement.item not in gaps:
                    gaps.append(requirement.item)
            elif requirement.evidence and not has_evidence:
                requirement = requirement.model_copy(update={"evidence": None})
            requirements.append(requirement)

        return response.model_copy(
            update={
                "contextual_requirements": requirements,
                "gaps": gaps,
                "improvement_suggestions": [
                    s for s in response.improvement_suggestions if self._is_safe_suggestion(s)
                ],
                "next_steps": [s for s in response.next_steps if self._is_safe_suggestion(s)],
            }
        )

    async def run(
        self,
        safe_request: AnalysisRequest,
        local_result: AnalysisResult,
        provider: AIProvider,
        sanitizer: SanitizerInterface | None = None,
    ) -> AIAnalysisResponse | None:
        sanitizer = sanitizer or PrivacySanitizer()
        resume = sanitizer.sanitize(safe_request.resume_text).text_sanitized
        job = sanitizer.sanitize(safe_request.job_text).text_sanitized
        safe = safe_request.model_copy(update={"resume_text": resume, "job_text": job})
        try:
            response_raw = await provider.generate_structured_analysis(safe, local_result)
            response = AIAnalysisResponse.model_validate(_response_json(response_raw))
            validated = self.apply_evidence_gate(response, resume, local_result)
            validated_content = json.dumps(validated.model_dump(), ensure_ascii=False)
            if sanitizer.sanitize(validated_content).items_removed:
                # The AI response still carried sanitizable content; reject it entirely
                # rather than risk leaking it, and let the caller fall back locally.
                return None
            return validated
        except AIProviderError:
            raise
        except Exception:
            return None


async def run_structured_ai_analysis(
    safe_request: AnalysisRequest,
    local_result: AnalysisResult,
    provider: AIProvider,
    sanitizer: SanitizerInterface | None = None,
) -> AIAnalysisResponse | None:
    return await StructuredAIAnalysisValidator().run(safe_request, local_result, provider, sanitizer)
