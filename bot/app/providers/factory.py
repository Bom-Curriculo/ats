import os
from pathlib import Path

from dotenv import load_dotenv

from app.providers.base import AIProviderError, AIProvider
from app.providers.deepseek import DeepSeekProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.mock import MockProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider

# O caminho explícito funciona mesmo quando o Uvicorn é iniciado na raiz do repositório
#
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def create_provider(nome: str | None = None) -> AIProvider:
    nome = (nome or os.getenv("IA_PROVIDER", "auto")).strip().lower()
    if nome == "mock":
        return MockProvider()
    if nome == "groq":
        return GroqProvider(
            chave_api=os.getenv("GROQ_API_KEY", ""),
            modelo=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )
    if nome == "ollama":
        return OllamaProvider(
            modelo=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if nome == "gemini":
        return GeminiProvider(
            chave_api=os.getenv("GEMINI_API_KEY", ""),
            modelo=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        )

    if nome == "deepseek":
        return DeepSeekProvider(
            chave_api=os.getenv("DEEPSEEK_API_KEY", ""),
            modelo=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        )

    if nome == "openai":
        return OpenAIProvider(
            chave_api=os.getenv("OPENAI_API_KEY", ""),
            modelo=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        )

    raise AIProviderError(
        f"Provedor '{nome}' não reconhecido. Use auto, mock, groq, ollama, "
        "gemini, deepseek ou openai."
    )
