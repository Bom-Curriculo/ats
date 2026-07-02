import asyncio

import pytest
from app.providers.base import ErroProvedorIA
from app.providers.mock import MockProvider
from app.schemas.analise import SolicitacaoAnalise
from app.services.gerenciador_ia import executar_analise_com_fallback


class ProviderFake(MockProvider):
    def __init__(self, nome: str, falhar: bool = False, capturas: list | None = None):

        super().__init__(modelo=f"modelo-{nome}", resumo=f"Resposta de {nome}.")

        self.nome = nome

        self.falhar = falhar

        self.capturas = capturas

    async def gerar_complemento(self, solicitacao, resultado_base):

        if self.capturas is not None:
            self.capturas.append((self.nome, solicitacao))

        if self.falhar:
            raise ErroProvedorIA(f"Falha simulada de {self.nome}")

        return await super().gerar_complemento(solicitacao, resultado_base)


def solicitacao() -> SolicitacaoAnalise:

    return SolicitacaoAnalise(
        curriculo_texto="COMPETÊNCIAS\nPython", vaga_texto="Requisitos:\nPython"
    )


def configurar_chaves(monkeypatch):

    for nome in ("GROQ", "GEMINI", "DEEPSEEK", "OPENAI"):
        monkeypatch.setenv(f"{nome}_API_KEY", "chave-ficticia-para-teste")


def test_auto_tenta_groq_primeiro(monkeypatch) -> None:

    configurar_chaves(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    chamadas = []

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: chamadas.append(nome) or ProviderFake(nome)
        )
    )

    assert chamadas == ["groq"]

    assert resultado.provedor_ia == "groq"

    assert resultado.fallback_ia.fallback_usado is False


def test_falha_groq_e_gemini_assume(monkeypatch) -> None:

    configurar_chaves(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: ProviderFake(nome, falhar=nome == "groq")
        )
    )

    assert resultado.provedor_ia == "gemini"

    assert resultado.fallback_ia.provedores_tentados == ["groq", "gemini"]

    assert resultado.fallback_ia.fallback_usado is True

    assert "Groq" in resultado.fallback_ia.ultimo_erro_sanitizado


def test_groq_sem_chave_e_ignorado(monkeypatch) -> None:

    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-para-teste")

    resultado = asyncio.run(
        executar_analise_com_fallback(solicitacao(), lambda nome: ProviderFake(nome))
    )

    assert resultado.provedor_ia == "gemini"
    assert resultado.fallback_ia.provedores_ignorados_por_configuracao == ["groq"]
    assert resultado.fallback_ia.provedores_tentados == ["gemini"]


def test_todos_falham_e_usam_fallback_local(monkeypatch) -> None:

    configurar_chaves(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: ProviderFake(nome, falhar=True)
        )
    )

    assert resultado.fallback_local_usado is True
    assert resultado.provedor_ia == "sem_ia"
    assert resultado.fallback_ia.provedores_tentados == ["groq", "gemini"]
    assert len(resultado.erros_provedores_sanitizados) == 2


@pytest.mark.parametrize(
    "selecionado,proibido", [("groq", "deepseek"), ("deepseek", "groq")]
)
def test_modo_explicito_tenta_somente_selecionado(
    monkeypatch, selecionado, proibido
) -> None:

    configurar_chaves(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", selecionado)

    chamadas = []

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: chamadas.append(nome) or ProviderFake(nome)
        )
    )

    assert chamadas == [selecionado]

    assert resultado.provedor_ia == selecionado

    assert proibido not in chamadas


def test_dados_sensiveis_chegam_sanitizados_a_todos_provedores(monkeypatch) -> None:

    configurar_chaves(monkeypatch)

    monkeypatch.setenv("IA_PROVIDER", "auto")

    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")

    capturas = []

    entrada = SolicitacaoAnalise(
        curriculo_texto="ana@example.com (81) 99999-1234 COMPETÊNCIAS: Python",
        vaga_texto="Requisitos: Python",
    )

    resultado = asyncio.run(
        executar_analise_com_fallback(
            entrada,
            lambda nome: ProviderFake(nome, falhar=nome == "groq", capturas=capturas),
        )
    )

    assert len(capturas) == 2

    for _, recebida in capturas:
        assert "ana@example.com" not in recebida.curriculo_texto

        assert "99999-1234" not in recebida.curriculo_texto

    assert resultado.privacidade.itens_removidos_antes_ia == ["email", "telefone"]


def test_json_invalido_tenta_proximo_provedor(monkeypatch) -> None:
    configurar_chaves(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    chamadas = []

    def fabrica(nome):
        chamadas.append(nome)
        if nome == "groq":
            provedor = MockProvider(resposta_estruturada="resposta sem JSON")
            provedor.nome = nome
            return provedor
        return ProviderFake(nome)

    resultado = asyncio.run(executar_analise_com_fallback(solicitacao(), fabrica))

    assert chamadas == ["groq", "gemini"]
    assert resultado.provedor_ia == "gemini"
    assert resultado.fallback_ia.fallback_usado is True
    assert "inválida" in resultado.erros_provedores_sanitizados[0]


def test_score_baixo_valido_nao_troca_provider(monkeypatch) -> None:
    configurar_chaves(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "auto")
    monkeypatch.setenv("IA_PROVIDER_CHAIN", "groq,gemini")
    chamadas = []
    entrada = SolicitacaoAnalise(
        curriculo_texto="COMPETÊNCIAS\nPython",
        vaga_texto="Requisitos obrigatórios:\nKubernetes",
    )

    resultado = asyncio.run(
        executar_analise_com_fallback(
            entrada, lambda nome: chamadas.append(nome) or ProviderFake(nome)
        )
    )

    assert resultado.pontuacao_ats == 0
    assert chamadas == ["groq"]
    assert resultado.provedor_ia == "groq"


def test_provider_explicito_falha_e_nao_tenta_outro(monkeypatch) -> None:
    configurar_chaves(monkeypatch)
    monkeypatch.setenv("IA_PROVIDER", "groq")
    chamadas = []

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(),
            lambda nome: chamadas.append(nome) or ProviderFake(nome, falhar=True),
        )
    )

    assert chamadas == ["groq"]
    assert resultado.fallback_local_usado is True
    assert resultado.provedor_ia == "sem_ia"


def test_usar_ia_padrao_false_nao_chama_provider(monkeypatch) -> None:
    monkeypatch.setenv("USAR_IA_PADRAO", "false")
    chamadas = []

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: chamadas.append(nome) or ProviderFake(nome)
        )
    )

    assert chamadas == []
    assert resultado.fallback_local_usado is True
    assert resultado.privacidade.texto_enviado_para_ia_foi_sanitizado is False


def test_erro_do_provider_nao_vaza_segredo_em_logs_ou_resultado(
    monkeypatch, caplog
) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    segredo = "Bearer token-super-secreto-123456789"

    class ProviderInseguro(ProviderFake):
        async def gerar_complemento(self, solicitacao, resultado_base):
            raise ErroProvedorIA(
                f"Authorization: {segredo}; prompt completo confidencial"
            )

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: ProviderInseguro(nome)
        )
    )
    serializado = resultado.model_dump_json()

    assert segredo not in caplog.text
    assert segredo not in serializado
    assert "Authorization" not in serializado
    assert "prompt completo confidencial" not in serializado


@pytest.mark.parametrize(
    "categoria,status",
    [
        ("auth_error_401", 401),
        ("permission_error_403", 403),
        ("rate_limit_429", 429),
        ("timeout", None),
    ],
)
def test_erro_groq_retorna_diagnostico_estruturado_sanitizado(
    monkeypatch, categoria, status
) -> None:
    monkeypatch.setenv("IA_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")

    class GroqComFalha(ProviderFake):
        async def gerar_complemento(self, solicitacao, resultado_base):
            raise ErroProvedorIA(
                "detalhe interno que não deve sair",
                categoria=categoria,
                status_http=status,
            )

    resultado = asyncio.run(
        executar_analise_com_fallback(
            solicitacao(), lambda nome: GroqComFalha(nome)
        )
    )
    detalhe = resultado.detalhes_erros_provedores[0]

    assert detalhe.provider == "groq"
    assert detalhe.categoria_erro == categoria
    assert detalhe.status_http == status
    assert "detalhe interno" not in resultado.model_dump_json()
