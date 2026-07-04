from app.providers.openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, key_api: str, model: str) -> None:
        super().__init__(
            name="openai",
            key_api=key_api,
            key_variable="OPENAI_API_KEY",
            model=model,
            url="https://api.openai.com/v1/chat/completions",
        )
