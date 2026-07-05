from app.providers.base import AIProvider
from app.models.analysis import AIComplement, AnalysisResult, AnalysisRequest


class MockProvider(AIProvider):
    name = "mock"

    def __init__(
        self,
        model: str = "modelo-mock",
        summary: str = "Resumo gerado pelo provedor de teste.",
        suggestions: list[str] | None = None,
        structured_response: dict | str | None = None,
        simulated_error: Exception | None = None,
        task_responses: dict[str, dict | str | Exception] | None = None,
    ) -> None:
        self.model = model
        self.summary = summary
        self.suggestions = suggestions or ["Sugestão gerada pelo provedor de teste."]
        self.structured_response = structured_response
        self.simulated_error = simulated_error
        self.task_responses = task_responses or {}
        self.task_prompts: list[tuple[str, str]] = []

    async def generate_completion(
        self,
        request: AnalysisRequest,
        base_result: AnalysisResult,
    ) -> AIComplement:
        return AIComplement(
            generated_summary=self.summary,
            suggestions=self.suggestions,
        )

    async def generate_structured_analysis(self, safe_request, local_result):
        if self.simulated_error is not None:
            raise self.simulated_error
        if self.structured_response is not None:
            return self.structured_response
        return await super().generate_structured_analysis(
            safe_request, local_result
        )

    async def run_structured_task(self, task, prompt, schema, temperature=0.1):
        self.task_prompts.append((task, prompt))
        response = self.task_responses.get(task)
        if isinstance(response, Exception):
            raise response
        if response is None:
            return None
        if isinstance(response, str):
            import json
            response = json.loads(response)
        return schema.model_validate(response).model_dump()
