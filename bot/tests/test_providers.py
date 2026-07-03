import asyncio
from pathlib import Path

import pytest
from dotenv import dotenv_values
from app.providers.base import AIProviderError
from app.providers.factory import create_provider
from app.providers.mock import MockProvider
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume_with_ai

"""testes sem chamar Groq ou Ollama, recomendação do GPT"""


def test_mock_aprimora_resultado_sem_alterar_pontuacao() -> None:

    solicitacao = AnalysisRequest(
        curriculo_texto="Experiência com Python.",
        vaga_texto="Python FastAPI",
        usar_ia=True,
    )

    provedor = MockProvider(
        resumo="Resumo controlado.",
        sugestoes=["Sugestão controlada."],
    )

    resultado = asyncio.run(analyze_resume_with_ai(solicitacao, provedor))

    # score é calculado local, mock so complementa resumo e sugestões
    assert resultado.pontuacao_ats == 50

    assert resultado.resumo_gerado == "Resumo controlado."

    assert resultado.sugestoes == ["Sugestão controlada."]

    assert resultado.provedor_ia == "mock"

    assert resultado.modelo_ia == "modelo-mock"


def test_groq_sem_chave_retorna_erro_claro(monkeypatch: pytest.MonkeyPatch) -> None:

    monkeypatch.setenv("IA_PROVIDER", "groq")

    # tira a chave pra forcar o erro
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(AIProviderError, match="GROQ_API_KEY"):
        create_provider()


def test_modelo_padrao_groq_e_gpt_oss(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.delenv("GROQ_MODEL", raising=False)

    provedor = create_provider("groq")

    assert provedor.modelo == "openai/gpt-oss-120b"


def test_modelo_groq_do_ambiente_tem_prioridade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    provedor = create_provider("groq")

    assert provedor.modelo == "llama-3.3-70b-versatile"


MODELOS_PADRAO = {
    "groq": ("GROQ_MODEL", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "gemini": ("GEMINI_MODEL", "GEMINI_API_KEY", "gemini-2.5-pro"),
    "deepseek": ("DEEPSEEK_MODEL", "DEEPSEEK_API_KEY", "deepseek-v4-flash"),
    "openai": ("OPENAI_MODEL", "OPENAI_API_KEY", "gpt-5.5"),
    "ollama": ("OLLAMA_MODEL", None, "qwen3:8b"),
}


@pytest.mark.parametrize("nome", MODELOS_PADRAO)
def test_defaults_dos_modelos_batem_com_env_example(monkeypatch, nome) -> None:
    variavel_modelo, variavel_chave, esperado = MODELOS_PADRAO[nome]
    monkeypatch.delenv(variavel_modelo, raising=False)
    if variavel_chave:
        monkeypatch.setenv(variavel_chave, "chave-ficticia-para-teste")

    provedor = create_provider(nome)
    exemplo = dotenv_values(Path(__file__).parents[1] / ".env.example")

    assert provedor.modelo == esperado
    assert exemplo[variavel_modelo] == esperado


@pytest.mark.parametrize("nome", MODELOS_PADRAO)
def test_variavel_de_ambiente_sobrescreve_default(monkeypatch, nome) -> None:
    variavel_modelo, variavel_chave, _ = MODELOS_PADRAO[nome]
    modelo_customizado = f"modelo-customizado-{nome}"
    monkeypatch.setenv(variavel_modelo, modelo_customizado)
    if variavel_chave:
        monkeypatch.setenv(variavel_chave, "chave-ficticia-para-teste")

    provedor = create_provider(nome)

    assert provedor.modelo == modelo_customizado


def test_provedor_desconhecido_retorna_erro(monkeypatch: pytest.MonkeyPatch) -> None:

    # seta um provider q n existe
    monkeypatch.setenv("IA_PROVIDER", "inexistente")

    with pytest.raises(AIProviderError, match="não reconhecido"):
        create_provider()


def test_auto_e_o_padrao_quando_variavel_nao_existe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    # sem setar nada o default é auto mas sem chave vai dar erro
    monkeypatch.delenv("IA_PROVIDER", raising=False)

    with pytest.raises(AIProviderError, match="auto"):
        create_provider()
