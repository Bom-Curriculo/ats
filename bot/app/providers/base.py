import json
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.ai_context import build_ai_context


class AIProviderError(RuntimeError):
    """Controlled provider configuration error."""

    def __init__(
        self,
        message: str,
        *,
        category: str = "unknown_provider_error",
        status_http: int | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.status_http = status_http


class AIProvider(ABC):
    """Provider-independent interface."""

    name: str
    model: str

    @abstractmethod
    async def generate_completion(
        self,
        request: AnalysisRequest,
        base_result: AnalysisResult,
    ) -> AIComplement:
        """resumo local"""

    async def generate_structured_analysis(
        self, safe_request: AnalysisRequest, local_result: AnalysisResult
    ) -> AIAnalysisResponse | dict | str:
        complemento = await self.generate_completion(safe_request, local_result)
        return {
            "contextual_summary": complemento.generated_summary,
            "contextual_requirements": [],
            "strengths": [],
            "gaps": [],
            "possible_blockers": [],
            "improvement_suggestions": complemento.suggestions,
            "next_steps": [],
            "anti_fabrication_alerts": [],
            "confidence": 50,
        }

    async def run_structured_task(
        self, task: str, prompt: str, schema: type, temperature: float = 0.1
    ) -> dict[str, Any] | None:
        return None


def create_prompt(
    request: AnalysisRequest,
    base_result: AnalysisResult,
) -> str:
    """Build one instruction and require a compact, predictable JSON response."""

    # Implementation note.
    data = build_ai_context(request, base_result)

    # Implementation note.
    schema = AIAnalysisResponse.model_json_schema()
    return (
        "Você é um especialista em currículos ATS e recrutamento. Analise o currículo sanitizado "
        "contra a vaga sanitizada. Retorne somente JSON válido no schema solicitado. Não use Markdown. "
        "Não invente experiências, tecnologia, curso, empresa, cargo, formação, idioma, cidade, "
        "disponibilidade, certificação, métrica ou project. Se algo não aparece no currículo, classifique "
        "como lacuna. Evidência parcial é relacionado_mas_nao_explicito; term sem contexto suficiente é "
        "encontrado_sem_contexto_claro. "
        "Não reintroduza telefone, e-mail, CPF, endereço, LinkedIn ou GitHub. "
        "Não mande declarar como experiência uma tecnologia absent; trate-a como lacuna. "
        "Não confunda Docker com Kubernetes, ChatGPT web com APIs de IA, nem GitHub com domínio de branches, pull requests e code review. "
        "Separe lacuna real de falta de descrição. Sugira estudo ou project quando não existir evidência. "
        "Evidência relacionada não é match direto. Open source é diferencial, não obrigação. "
        "Curso é evidência educacional, nunca experiência profissional. Para estágio/júnior, courses e projects "
        "têm peso relevante e ausência de experiência profissional não reprova automaticamente. Para pleno/sênior, "
        "curso sem aplicação prática tem peso baixo e experiência real, produção, impacto e colaboração pesam mais. "
        "Frameworks podem implicar linguagens (Spring Boot/Java, FastAPI/Python, Laravel/PHP, Next.js/React), "
        "mas isso não implica experiência prática. Não marque HTML5 missing_items se HTML existe, nem CSS3 missing_items se CSS existe. "
        "Não marque APIs REST missing_items se há API REST em project, resumo ou competências. Spring Boot apenas em curso "
        "é encontrado_sem_contexto_claro, não encontrado_com_evidencia. Quando houver dúvida, use "
        "relacionado_mas_nao_explicito. Experiência pode ser parcialmente compensada por projects pessoais, acadêmicos, courses práticos, "
        "residência tecnológica, laboratórios e portfólio. Competências Técnicas é fortemente recomendada "
        "para ATS tech, mas sua ausência não reprova automaticamente. Diferencie adjustments imediatos, lacunas "
        "técnicas, possíveis impeditivos e próximos passos. Seja específico, direto, honesto e escreva em português do Brasil. "
        "Não peça para o usuário mentir. Não reproduza dados pessoais. Schema: "
        f"{json.dumps(schema, ensure_ascii=False)} Dados seguros:\n{json.dumps(data, ensure_ascii=False)}"
    )
