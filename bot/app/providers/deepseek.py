from app.providers.openai_compatible import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):

    def __init__(self, key_api: str, model: str) -> None:
        super().__init__(
            name="deepseek",
            key_api=key_api,
            key_variable="DEEPSEEK_API_KEY",
            model=model,
            url="https://api.deepseek.com/chat/completions",
        )
