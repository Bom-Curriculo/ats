from app.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, chave_api: str, modelo: str) -> None:
        super().__init__(
            nome="groq",
            chave_api=chave_api,
            variavel_chave="GROQ_API_KEY",
            modelo=modelo,
            url="https://api.groq.com/openai/v1/chat/completions",
        )
