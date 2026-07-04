from app.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, key_api: str, model: str) -> None:
        super().__init__(
            name="groq",
            key_api=key_api,
            key_variable="GROQ_API_KEY",
            model=model,
            url="https://api.groq.com/openai/v1/chat/completions",
        )
