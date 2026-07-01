import asyncio

from app.providers.mock import MockProvider
from app.schemas.analise import SolicitacaoAnalise
from app.services.analisador_ats import analisar_curriculo_com_ia
from app.services.analisador_ats import analisar_curriculo


def resposta_ia(**alteracoes):
    base = {
        "resumo_contextual": "Há aderência parcial comprovada.",
        "requisitos_contextuais": [],
        "pontos_fortes": ["Experiência descrita com Python."],
        "lacunas": [],

        "possiveis_impeditivos": [],
        "sugestoes_de_melhoria": ["Detalhe o contexto de uso de Python."],
        "proximos_passos": ["Confirme habilidades antes de adicioná-las."],
        "alertas_contra_inventar": ["Não declarar competências ausentes."],
        "confianca": 80,

        "score_sugerido_ia": 95,
        "justificativa_score_ia": "Leitura contextual complementar.",
    }
    base.update(alteracoes)
    return base


def test_json_valido_e_incorporado_sem_sobrescrever_score_local() -> None:
    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Experiência com Python.", vaga_texto="Python e FastAPI"
    )
    local_score = 50
    resultado = asyncio.run(
        analisar_curriculo_com_ia(
            solicitacao, MockProvider(resposta_estruturada=resposta_ia())
        )
    )
    assert resultado.pontuacao_ats == local_score
    assert resultado.score_sugerido_ia == 95
    assert resultado.analise_ia is not None
    assert resultado.fallback_local_usado is False


def test_json_invalido_usa_fallback_local() -> None:
    solicitacao = SolicitacaoAnalise(curriculo_texto="Python", vaga_texto="Python")
    score_local = analisar_curriculo(solicitacao).pontuacao_ats
    resultado = asyncio.run(
        analisar_curriculo_com_ia(
            solicitacao,
            MockProvider(resposta_estruturada="não é json"),
        )
    )

    # fallback local é usado quando a resposta não é JSON válido
    assert resultado.fallback_local_usado is True
    assert resultado.analise_ia is None
    assert resultado.pontuacao_ats == score_local


def test_evidence_gate_rebaixa_tecnologia_inventada() -> None:
    requisito = {
        "item": "Kubernetes",
        "categoria": "ferramenta",
        "importancia": "obrigatorio",
        "status": "encontrado_com_evidencia",
        "evidencia": "Administrou Kubernetes",
        "justificativa": "Suposta experiência.",
        "recomendacao": "Destacar Kubernetes.",
    }
    resultado = asyncio.run(
        analisar_curriculo_com_ia(
            SolicitacaoAnalise(curriculo_texto="Experiência com Python", vaga_texto="Kubernetes"),
            MockProvider(
                resposta_estruturada=resposta_ia(requisitos_contextuais=[requisito])
            ),
        )
    )
    validado = resultado.requisitos_contextuais[0]
    assert validado.status == "faltando"
    assert validado.evidencia is None
    assert "Kubernetes" in resultado.lacunas_contextuais


class MockCaptura(MockProvider):
    recebida = None

    async def gerar_analise_estruturada(self, solicitacao_segura, resultado_local):
        self.recebida = solicitacao_segura
        return resposta_ia()


def test_fronteira_remove_pii_links_e_tokens_de_curriculo_e_vaga() -> None:
    provedor = MockCaptura()
    segredo = "Bearer abcdefghijklmnopqrstuvwxyz123456"

    resultado = asyncio.run(

        analisar_curriculo_com_ia(
            SolicitacaoAnalise(
                curriculo_texto=(
                    "ana@example.com (81) 99999-1234 CPF 123.456.789-10 "

                    "https://linkedin.com/in/ana " + segredo
                ),
                vaga_texto="Contato recrutador@example.com https://empresa.example/vaga",
            ),
            provedor,
        )
    )
    enviado = provedor.recebida.curriculo_texto + provedor.recebida.vaga_texto
    #pii não vaza pro provider
    for valor in ("ana@example.com", "99999-1234", "123.456.789-10", "linkedin.com", segredo, "recrutador@example.com", "empresa.example"):
        assert valor not in enviado
    assert resultado.privacidade.texto_enviado_para_ia_foi_sanitizado is True
