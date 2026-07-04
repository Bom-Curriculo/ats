"""Generic AI provider backed by LangChain's ``init_chat_model``.

One class handles every supported provider (Groq, Gemini, DeepSeek, OpenAI,
Ollama) by delegating the actual HTTP/SDK work to LangChain's chat-model
integrations and their built-in structured-output support, instead of each
provider hand-rolling HTTP requests and JSON parsing.
"""

from langchain.chat_models import init_chat_model

from app.models.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.models.ai_analysis import AIAnalysisResponse
from app.providers.base import AIProvider, AIProviderError, create_prompt
from app.providers.error_mapping import map_provider_error

_MODEL_PROVIDERS = {
    "groq": "groq",
    "gemini": "google_genai",
    "deepseek": "deepseek",
    "openai": "openai",
    "ollama": "ollama",
}


class LangChainProvider(AIProvider):
    """AI provider whose transport is entirely delegated to LangChain."""

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str = "",
        base_url: str | None = None,
        timeout: float = 120.0,
        output_language: str = "pt-BR",
    ) -> None:
        if name not in _MODEL_PROVIDERS:
            raise AIProviderError(f"Unsupported provider '{name}'.", category="invalid_model")
        if name != "ollama" and not api_key.strip():
            raise AIProviderError(f"The {name} provider has no API key configured.", category="missing_api_key")

        self.name = name
        self.model = model
        self.output_language = output_language
        self._chat_model = init_chat_model(
            model,
            model_provider=_MODEL_PROVIDERS[name],
            **self._transport_kwargs(name, api_key, base_url, timeout),
        )

    @staticmethod
    def _transport_kwargs(name: str, api_key: str, base_url: str | None, timeout: float) -> dict:
        if name == "ollama":
            return {"base_url": base_url, "client_kwargs": {"timeout": timeout}}
        return {"api_key": api_key, "timeout": timeout}

    async def generate_completion(
        self,
        request: AnalysisRequest,
        base_result: AnalysisResult,
    ) -> AIComplement:
        analysis = await self.generate_structured_analysis(request, base_result)
        return AIComplement(
            generated_summary=analysis.contextual_summary,
            suggestions=analysis.improvement_suggestions + analysis.next_steps,
        )

    async def generate_structured_analysis(self, request, base_result) -> AIAnalysisResponse:
        prompt = create_prompt(request, base_result, self.output_language)
        return await self._invoke_structured(prompt, AIAnalysisResponse, temperature=0.2)

    async def run_structured_task(self, task: str, prompt: str, schema: type, temperature: float = 0.1) -> dict:
        result = await self._invoke_structured(prompt, schema, temperature=temperature)
        return result.model_dump()

    async def _invoke_structured(self, prompt: str, schema: type, temperature: float):
        structured_model = self._chat_model.bind(temperature=temperature).with_structured_output(schema)
        try:
            result = await structured_model.ainvoke(prompt)
        except Exception as error:
            raise map_provider_error(self.name, error) from error
        if result is None:
            raise AIProviderError(f"{self.name.capitalize()} returned an empty response.", category="empty_response")
        return result
