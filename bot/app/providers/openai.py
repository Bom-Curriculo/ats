from app.providers.compativel_openai import ProviderCompativelOpenAI


class OpenAIProvider(ProviderCompativelOpenAI):
    def __init__(self, chave_api: str, modelo: str) -> None:
        super().__init__(
            nome="openai",
            chave_api=chave_api,
            variavel_chave="OPENAI_API_KEY",
            modelo=modelo,
            url="https://api.openai.com/v1/chat/completions",
        )
