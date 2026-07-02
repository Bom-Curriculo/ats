import asyncio

from app.providers.base import criar_prompt
from app.providers.mock import MockProvider
from app.schemas.analise import SolicitacaoAnalise
from app.services.analisador_ats import analisar_curriculo_com_ia
from app.services.normalizador_texto import normalizar_texto_curriculo
from app.services.sanitizador_privacidade import sanitizar_dados_pessoais

"""Casos de privacidade e limpeza de texto extraído de PDF"""


def test_sanitizador_remove_email_e_telefone_sem_devolver_originais() -> None:

    email = "ana.teste@example.com"

    telefone = "(81) 99999-1234"

    resultado = sanitizar_dados_pessoais(f"Contato: {email} ou {telefone}")

    # trocou corretamente pelos marcadores
    assert (
        resultado.texto_sanitizado == "Contato: [EMAIL_REMOVIDO] ou [TELEFONE_REMOVIDO]"
    )

    assert resultado.itens_removidos == ["email", "telefone"]

    # garante q os dados originais não
    assert email not in repr(resultado)

    assert telefone not in repr(resultado)


def test_normalizador_corrige_titulo_espacado() -> None:

    assert normalizar_texto_curriculo("C O M P E T Ê N C I A S") == "COMPETÊNCIAS"


class ProvedorCaptura(MockProvider):
    solicitacao_recebida: SolicitacaoAnalise | None = None

    async def gerar_complemento(self, solicitacao, resultado_base):

        # captura a solicitação recebida para inspecionar depois
        self.solicitacao_recebida = solicitacao

        return await super().gerar_complemento(solicitacao, resultado_base)


def test_ia_recebe_apenas_curriculo_sanitizado() -> None:

    provedor = ProvedorCaptura()

    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Ana, ana@example.com, (81) 99999-1234. Experiência: React.",
        vaga_texto="Requisitos obrigatórios:\nReact",
        usar_ia=True,
    )

    resultado = asyncio.run(analisar_curriculo_com_ia(solicitacao, provedor))

    assert provedor.solicitacao_recebida is not None

    # provedor nunca pode ver dados reais
    assert "ana@example.com" not in provedor.solicitacao_recebida.curriculo_texto

    assert "99999-1234" not in provedor.solicitacao_recebida.curriculo_texto

    assert resultado.privacidade is not None

    assert resultado.privacidade.texto_enviado_para_ia_foi_sanitizado is True

    assert resultado.privacidade.itens_removidos_antes_ia == ["email", "telefone"]


def test_prompt_aplica_defesa_em_profundidade() -> None:

    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Contato ana@example.com e experiência com React.",
        vaga_texto="React",
    )

    from app.services.analisador_ats import analisar_curriculo

    prompt = criar_prompt(solicitacao, analisar_curriculo(solicitacao))

    # msm q alguem chame o builder direto, o prompt sanitiza dnv
    assert "ana@example.com" not in prompt

    assert "[EMAIL_REMOVIDO]" in prompt

    # garantir que a instrução do prompt está lá
    assert "Não invente experiências" in prompt


def test_prompt_remove_todos_identificadores_ficticios() -> None:
    pessoais = (
        "teste@example.com",
        "(81) 99999-1234",
        "https://linkedin.com/in/teste",
        "https://github.com/teste",
        "https://portfolio-teste.example.com",
    )
    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Contato: " + " ".join(pessoais) + " HABILIDADES: Python",
        vaga_texto="Requisitos: Python",
    )
    from app.services.analisador_ats import analisar_curriculo

    prompt = criar_prompt(solicitacao, analisar_curriculo(solicitacao))

    assert not any(valor in prompt for valor in pessoais)
