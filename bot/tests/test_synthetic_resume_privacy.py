import asyncio
import json

from app.providers.mock import MockProvider
from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume, analyze_resume_with_ai
from app.services.privacy_sanitizer import sanitize_personal_data


CURRICULO_FAKE = """Pessoa Exemplo
E-mail: pessoa.teste@gmail.example
Telefone: (81) 99999-1234
CPF: 123.456.789-09
LinkedIn: https://linkedin.com/in/pessoa-exemplo
GitHub: https://github.com/pessoa-exemplo
Portfólio: https://portfolio.example.dev
Endereço: Rua Exemplo, 123, Bairro Teste
PROJETOS
Serviço Web
Stack: Python 3.12, FastAPI, .NET 9, Java 17
- API publicada com testes
Repositório: https://github.com/pessoa-exemplo/servico-web
Deploy: https://servico-web.vercel.app
FORMAÇÃO
Curso Superior | 2020 - 2023
"""


def test_sanitizacao_classifica_links_sem_retornar_valores():
    resultado = sanitize_personal_data(CURRICULO_FAKE)
    assert {"email", "telefone", "cpf", "linkedin_url", "github_profile_url",
            "portfolio_url", "github_repo_url", "deploy_url", "endereco"} <= set(resultado.itens_removidos)
    assert resultado.links_detectados_por_tipo == {
        "linkedin_url": 1, "github_profile_url": 1, "portfolio_url": 1,
        "github_repo_url": 1, "deploy_url": 1,
    }
    for valor in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "portfolio.example.dev", "vercel.app", "Rua Exemplo"):
        assert valor not in resultado.texto_sanitizado
    assert "[EMAIL_REMOVIDO]" in resultado.texto_sanitizado
    assert "[PORTFOLIO_REMOVIDO]" in resultado.texto_sanitizado
    assert "[URL_REMOVIDA]" in resultado.texto_sanitizado


def test_sanitizacao_preserva_datas_versoes_e_tecnologias():
    seguro = sanitize_personal_data(CURRICULO_FAKE).texto_sanitizado
    for valor in ("2020 - 2023", ".NET 9", "Java 17", "Python 3.12", "FastAPI"):
        assert valor in seguro


class MockCapturaSeguro(MockProvider):
    recebida = None

    async def gerar_analise_estruturada(self, solicitacao_segura, resultado_local):
        self.recebida = solicitacao_segura
        return {
            "resumo_contextual": "Análise segura.", "requisitos_contextuais": [],
            "pontos_fortes": ["Python"], "lacunas": [], "possiveis_impeditivos": [],
            "sugestoes_de_melhoria": ["Detalhe o projeto real."], "proximos_passos": [],
            "alertas_contra_inventar": ["Não invente."], "confianca": 80,
        }


def test_provider_recebe_somente_texto_sanitizado_e_sem_fontes_brutas():
    provedor = MockCapturaSeguro()
    entrada = AnalysisRequest(
        curriculo_texto=CURRICULO_FAKE,
        vaga_texto="Contato: recrutador@example.com\nRequisitos: Python e FastAPI",
        fontes_curriculo=[{"tipo": "github_url", "url": "https://github.com/pessoa-exemplo"}],
    )
    resultado = asyncio.run(analyze_resume_with_ai(entrada, provedor))
    enviado = provedor.recebida.curriculo_texto + provedor.recebida.vaga_texto
    assert provedor.recebida.fontes_curriculo == []
    for valor in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "recrutador@example.com"):
        assert valor not in enviado
    assert resultado.privacidade.texto_enviado_para_ia_foi_sanitizado is True


def test_resposta_local_nao_devolve_pii_e_mantem_analise_tecnica():
    resultado = analyze_resume(AnalysisRequest(
        curriculo_texto=CURRICULO_FAKE, vaga_texto="Requisitos: Python, FastAPI, .NET e Java"
    ))
    serializado = json.dumps(resultado.model_dump(), ensure_ascii=False)
    for valor in ("pessoa.teste@gmail.example", "99999-1234", "123.456.789-09",
                  "linkedin.com", "github.com", "portfolio.example.dev", "Rua Exemplo"):
        assert valor not in serializado
    assert {"Python", "FastAPI", ".NET", "Java"} <= set(resultado.palavras_chave_encontradas)
    resumo = resultado.sanitizacao_resumo
    assert resumo["dados_sensiveis_detectados"] is True
    assert resumo["quantidade_categorias"] >= 5
    assert resumo["links_detectados_por_tipo"]["github_repo_url"] == 1
    assert "pessoa" not in resumo["observacao_segura"].casefold()


def test_fontes_textuais_futuras_mantem_contrato_aditivo():
    entrada = AnalysisRequest(
        fontes_curriculo=[{"tipo": "curriculo_texto", "conteudo": "PROJETOS\nAPI\nStack: Python"}],
        vaga_texto="Requisitos: Python",
    )
    assert "Python" in entrada.curriculo_texto
    resultado = analyze_resume(entrada)
    assert "Python" in resultado.palavras_chave_encontradas
