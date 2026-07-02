from app.providers.compativel_openai import ProviderCompativelOpenAI


class DeepSeekProvider(ProviderCompativelOpenAI):

    def __init__(self, chave_api: str, modelo: str) -> None:
        super().__init__(
            nome="deepseek",
            chave_api=chave_api,
            variavel_chave="DEEPSEEK_API_KEY",
            modelo=modelo,
            url="https://api.deepseek.com/chat/completions",
        )
