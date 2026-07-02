from app.providers.compativel_openai import ProviderCompativelOpenAI


class GroqProvider(ProviderCompativelOpenAI):
    def __init__(self, chave_api: str, modelo: str) -> None:
        super().__init__(
            nome="groq",
            chave_api=chave_api,
            variavel_chave="GROQ_API_KEY",
            modelo=modelo,
            url="https://api.groq.com/openai/v1/chat/completions",
        )
