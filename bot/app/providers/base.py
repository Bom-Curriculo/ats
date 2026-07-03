import json
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.ai_context import build_ai_context


class AIProviderError(RuntimeError):
    """erro controlado de conf"""

    def __init__(
        self,
        mensagem: str,
        *,
        categoria: str = "unknown_provider_error",
        status_http: int | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.categoria = categoria
        self.status_http = status_http


class AIProvider(ABC):
    """nção depender do fornecedor"""

    nome: str
    modelo: str

    @abstractmethod
    async def gerar_complemento(
        self,
        solicitacao: AnalysisRequest,
        resultado_base: AnalysisResult,
    ) -> AIComplement:
        """resumo local"""

    async def gerar_analise_estruturada(
        self, solicitacao_segura: AnalysisRequest, resultado_local: AnalysisResult
    ) -> AIAnalysisResponse | dict | str:
        complemento = await self.gerar_complemento(solicitacao_segura, resultado_local)
        return {
            "resumo_contextual": complemento.resumo_gerado,
            "requisitos_contextuais": [],
            "pontos_fortes": [],
            "lacunas": [],
            "possiveis_impeditivos": [],
            "sugestoes_de_melhoria": complemento.sugestoes,
            "proximos_passos": [],
            "alertas_contra_inventar": [],
            "confianca": 50,
        }

    async def executar_tarefa_estruturada(
        self, tarefa: str, prompt: str, schema: type, temperatura: float = 0.1
    ) -> dict[str, Any] | None:
        return None


def create_prompt(
    solicitacao: AnalysisRequest,
    resultado_base: AnalysisResult,
) -> str:
    """Monta uma instrução única e exige uma resposta JSON pequena e previsível."""

    # Defesa em profundidade: mesmo uma chamada direta ao builder não inclui PII
    dados = build_ai_context(solicitacao, resultado_base)

    # monta instrução pro modelo
    schema = AIAnalysisResponse.model_json_schema()
    return (
        "Você é um especialista em currículos ATS e recrutamento. Analise o currículo sanitizado "
        "contra a vaga sanitizada. Retorne somente JSON válido no schema solicitado. Não use Markdown. "
        "Não invente experiências, tecnologia, curso, empresa, cargo, formação, idioma, cidade, "
        "disponibilidade, certificação, métrica ou projeto. Se algo não aparece no currículo, classifique "
        "como lacuna. Evidência parcial é relacionado_mas_nao_explicito; termo sem contexto suficiente é "
        "encontrado_sem_contexto_claro. "
        "Não reintroduza telefone, e-mail, CPF, endereço, LinkedIn ou GitHub. "
        "Não mande declarar como experiência uma tecnologia ausente; trate-a como lacuna. "
        "Não confunda Docker com Kubernetes, ChatGPT web com APIs de IA, nem GitHub com domínio de branches, pull requests e code review. "
        "Separe lacuna real de falta de descrição. Sugira estudo ou projeto quando não existir evidência. "
        "Evidência relacionada não é match direto. Open source é diferencial, não obrigação. "
        "Curso é evidência educacional, nunca experiência profissional. Para estágio/júnior, cursos e projetos "
        "têm peso relevante e ausência de experiência profissional não reprova automaticamente. Para pleno/sênior, "
        "curso sem aplicação prática tem peso baixo e experiência real, produção, impacto e colaboração pesam mais. "
        "Frameworks podem implicar linguagens (Spring Boot/Java, FastAPI/Python, Laravel/PHP, Next.js/React), "
        "mas isso não implica experiência prática. Não marque HTML5 faltando se HTML existe, nem CSS3 faltando se CSS existe. "
        "Não marque APIs REST faltando se há API REST em projeto, resumo ou competências. Spring Boot apenas em curso "
        "é encontrado_sem_contexto_claro, não encontrado_com_evidencia. Quando houver dúvida, use "
        "relacionado_mas_nao_explicito. Experiência pode ser parcialmente compensada por projetos pessoais, acadêmicos, cursos práticos, "
        "residência tecnológica, laboratórios e portfólio. Competências Técnicas é fortemente recomendada "
        "para ATS tech, mas sua ausência não reprova automaticamente. Diferencie ajustes imediatos, lacunas "
        "técnicas, possíveis impeditivos e próximos passos. Seja específico, direto, honesto e escreva em português do Brasil. "
        "Não peça para o usuário mentir. Não reproduza dados pessoais. Schema: "
        f"{json.dumps(schema, ensure_ascii=False)} Dados seguros:\n{json.dumps(dados, ensure_ascii=False)}"
    )
