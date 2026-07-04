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

# Technical note removed during English standardization.
#
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def create_provider(name: str | None = None) -> AIProvider:
    name = (name or os.getenv("IA_PROVIDER", "auto")).strip().lower()
    if name == "mock":
        return MockProvider()
    if name == "groq":
        return GroqProvider(
            key_api=os.getenv("GROQ_API_KEY", ""),
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )
    if name == "ollama":
        return OllamaProvider(
            model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if name == "gemini":
        return GeminiProvider(
            key_api=os.getenv("GEMINI_API_KEY", ""),
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        )

    if name == "deepseek":
        return DeepSeekProvider(
            key_api=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        )

    if name == "openai":
        return OpenAIProvider(
            key_api=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        )

    raise AIProviderError(
        f"Provedor '{name}' não reconhecido. Use auto, mock, groq, ollama, "
        "gemini, deepseek ou openai."
    )
