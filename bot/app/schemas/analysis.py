from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.ai_analysis import AIRequirementAnalysis, AIAnalysisResponse
from app.schemas.ai_pipeline import (
    ContextualRequirementEvaluation,
    AIJobClassification,
    SelectedEvidence,
    AIPipelineResult,
)


ResumeSourceType = Literal["curriculo_texto", "curriculo_pdf", "linkedin_pdf", "linkedin_text",
    "linkedin_url", "github_url", "portfolio_url", "portfolio_text", "vaga_texto", "vaga_url",
    "informacoes_pessoais", "instrucoes_customizadas"]


class ResumeSource(BaseModel):
    tipo: ResumeSourceType
    conteudo: str | None = None
    url: str | None = None


class AnalysisRequest(BaseModel):
    resume_text: str = Field(
        default="",
        validation_alias=AliasChoices("resume_text", "curriculo_texto"),
        serialization_alias="curriculo_texto",
        description="Full resume text",
    )

    job_text: str = Field(
        min_length=1,
        validation_alias=AliasChoices("job_text", "vaga_texto"),
        serialization_alias="vaga_texto",
        description="Full job description",
    )

    language: str = Field(
        default="pt-BR",
        min_length=2,
        validation_alias=AliasChoices("language", "idioma"),
        serialization_alias="idioma",
    )

    # Retained as an optional switch for compatibility with existing clients.
    use_ai: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("use_ai", "usar_ia"),
        serialization_alias="usar_ia",
    )

    job_level: str | None = Field(
        default=None,
        validation_alias=AliasChoices("job_level", "nivel_vaga"),
        serialization_alias="nivel_vaga",
    )
    resume_sources: list[ResumeSource] = Field(
        default_factory=list,
        validation_alias=AliasChoices("resume_sources", "fontes_curriculo"),
        serialization_alias="fontes_curriculo",
    )

    @model_validator(mode="after")
    def consolidate_text_sources(self):
        if not self.resume_text.strip():
            text_source_types = {"curriculo_texto", "linkedin_text", "portfolio_text", "informacoes_pessoais", "instrucoes_customizadas"}
            texts = [source.conteudo.strip() for source in self.resume_sources
                     if source.tipo in text_source_types and source.conteudo and source.conteudo.strip()]
            if not texts:
                raise ValueError("curriculo_texto ou uma fonte textual de currículo é obrigatório")
            self.resume_text = "\n\n".join(texts)
        return self

    # Python attribute compatibility during the deprecation window.
    @property
    def curriculo_texto(self) -> str:
        return self.resume_text

    @property
    def vaga_texto(self) -> str:
        return self.job_text

    @property
    def idioma(self) -> str:
        return self.language

    @property
    def usar_ia(self) -> bool | None:
        return self.use_ai

    @property
    def nivel_vaga(self) -> str | None:
        return self.job_level

    @property
    def fontes_curriculo(self) -> list[ResumeSource]:
        return self.resume_sources

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "curriculo_texto": "texto do currículo",
                "vaga_texto": "texto da vaga",
                "idioma": "pt-BR",
            }
        }
    )


class PrivacyInformation(BaseModel):
    """Metadados seguros sobre o tratamento anterior à chamada de IA."""

    dados_sensiveis_detectados: bool = False

    itens_removidos_antes_ia: list[str] = Field(default_factory=list)

    texto_enviado_para_ia_foi_sanitizado: bool = False


class DetailedAnalysis(BaseModel):
    """Classificação das correspondências pra vaga"""

    requisitos_obrigatorios_encontrados: list[str] = Field(default_factory=list)

    requisitos_obrigatorios_faltando: list[str] = Field(default_factory=list)

    diferenciais_encontrados: list[str] = Field(default_factory=list)

    diferenciais_faltando: list[str] = Field(default_factory=list)

    tecnologias_encontradas: list[str] = Field(default_factory=list)

    tecnologias_faltando: list[str] = Field(default_factory=list)

    possiveis_impeditivos: list[str] = Field(default_factory=list)


class DetailedSuggestions(BaseModel):
    """separa sem pressupor experiência."""

    ajustes_recomendados: list[str] = Field(default_factory=list)

    lacunas_tecnicas: list[str] = Field(default_factory=list)

    pontos_de_atencao: list[str] = Field(default_factory=list)

    proximos_passos: list[str] = Field(default_factory=list)

    ajustes_no_curriculo: list[str] = Field(default_factory=list)
    lacunas_reais: list[str] = Field(default_factory=list)
    proximos_passos_de_estudo: list[str] = Field(default_factory=list)
    alertas_contra_inventar: list[str] = Field(default_factory=list)


class RequirementAnalysisItem(BaseModel):
    """para cada item da vaga é uma solução"""

    item: str

    tipo: str

    categoria: str

    peso: int

    status: str

    evidencia_no_curriculo: str | None = None

    orientacao: str

    nivel_evidencia: str = "sem_evidencia"

    fonte_evidencia: str | None = None

    forca_inferencia: str | None = None


class ResumeEvidence(BaseModel):
    experiencia_profissional: bool = False

    projetos_pessoais: bool = False

    projetos_academicos: bool = False

    open_source: bool = False

    cursos: bool = False

    residencia_tecnologica: bool = False

    secao_habilidades: bool = False


class AIFallback(BaseModel):
    """tentativas de provedores"""

    fallback_usado: bool = False

    provedores_tentados: list[str] = Field(default_factory=list)

    provedores_ignorados_por_configuracao: list[str] = Field(default_factory=list)

    ultimo_erro_sanitizado: str | None = None

    erros_provedores_sanitizados: list[str] = Field(default_factory=list)


class SanitizedProviderError(BaseModel):
    provider: str
    modelo: str | None = None
    categoria_erro: str
    status_http: int | None = None
    mensagem_segura: str


class ItemKeyword(BaseModel):
    termo: str
    categoria: str
    peso: float
    presente: bool
    fonte: str | None = None


class KeywordReport(BaseModel):
    hard_skills: list[ItemKeyword] = Field(default_factory=list)
    title_function_keywords: list[ItemKeyword] = Field(default_factory=list)
    business_context: list[ItemKeyword] = Field(default_factory=list)
    action_keywords: list[ItemKeyword] = Field(default_factory=list)
    domain_keywords: list[ItemKeyword] = Field(default_factory=list)
    hard_filters: list[ItemKeyword] = Field(default_factory=list)
    alertas_hard_filters: list[str] = Field(default_factory=list)


class FactBank(BaseModel):
    experiencias: list[dict] = Field(default_factory=list)
    projetos: list[dict] = Field(default_factory=list)
    cursos: list[dict] = Field(default_factory=list)
    skills: list[dict] = Field(default_factory=list)
    idiomas: list[dict] = Field(default_factory=list)
    projetos_academicos: list[dict] = Field(default_factory=list)
    freelas: list[dict] = Field(default_factory=list)
    open_source: list[dict] = Field(default_factory=list)
    residencias: list[dict] = Field(default_factory=list)
    certificacoes: list[dict] = Field(default_factory=list)
    conquistas: list[dict] = Field(default_factory=list)
    tecnologias_por_fonte: dict[str, list[str]] = Field(default_factory=dict)
    evidencias: list[dict] = Field(default_factory=list)


class RequirementGroup(BaseModel):
    nome: str
    tipo: str
    modo: str
    itens: list[str] = Field(default_factory=list)
    status_grupo: str
    evidencia_resumida: str | None = None
    impacto_score: float = 0
    justificativa: str | None = None


class AnalysisResult(BaseModel):
    """resu8ltado que é consumido"""

    pontuacao_ats: int = Field(ge=0, le=100)

    palavras_chave_encontradas: list[str]

    palavras_chave_faltando: list[str]

    problemas_detectados: list[str]

    sugestoes: list[str]

    resumo_gerado: str

    provedor_ia: str = "sem_ia"

    modelo_ia: str | None = None

    privacidade: PrivacyInformation | None = None

    analise_detalhada: DetailedAnalysis | None = None

    sugestoes_detalhadas: DetailedSuggestions | None = None

    analise_valida: bool = True

    alertas_entrada: list[str] = Field(default_factory=list)

    inventario_curriculo: dict[str, list[str]] | None = None

    analise_por_requisito: list[RequirementAnalysisItem] = Field(default_factory=list)

    evidencias: ResumeEvidence | None = None

    explicacao_matching: str = ""

    fallback_ia: AIFallback | None = None

    analise_ia: AIAnalysisResponse | None = None
    score_sugerido_ia: int | None = Field(default=None, ge=0, le=100)
    justificativa_score_ia: str | None = None
    confianca_ia: int | None = Field(default=None, ge=0, le=100)
    fallback_local_usado: bool = False
    requisitos_contextuais: list[AIRequirementAnalysis] = Field(default_factory=list)
    lacunas_contextuais: list[str] = Field(default_factory=list)
    proximos_passos: list[str] = Field(default_factory=list)
    alertas_contra_inventar: list[str] = Field(default_factory=list)
    provedores_tentados: list[str] = Field(default_factory=list)
    erros_provedores_sanitizados: list[str] = Field(default_factory=list)
    detalhes_erros_provedores: list[SanitizedProviderError] = Field(default_factory=list)
    nivel_vaga: str = "nao_informado"
    validacao_ia_aplicada: bool = False
    ajustes_validacao_ia: list[str] = Field(default_factory=list)
    score_final_recomendado: int | None = Field(default=None, ge=0, le=100)
    explicacao_score_final: str | None = None
    keyword_report: KeywordReport | None = None
    score_keyword_coverage: int | None = Field(default=None, ge=0, le=100)
    keywords_presentes_ponderadas: list[ItemKeyword] = Field(default_factory=list)
    keywords_ausentes_ponderadas: list[ItemKeyword] = Field(default_factory=list)
    explicacao_keyword_coverage: str | None = None
    fact_bank: FactBank | None = None
    papel_ia: list[str] = Field(default_factory=list)
    qualidade_contexto_ia: int | None = Field(default=None, ge=0, le=100)
    avaliacao_relevancia: dict | None = None
    matriz_evidencia: list[dict] = Field(default_factory=list)
    lacunas_priorizadas: list[dict] = Field(default_factory=list)
    sugestoes_de_reescrita_seguras: list[str] = Field(default_factory=list)
    diagnostico_ats: dict | None = None
    score_contextual_ia: int | None = Field(default=None, ge=0, le=100)
    fatores_score_final: dict[str, float | int | str | bool] = Field(default_factory=dict)
    alertas_score_final: list[str] = Field(default_factory=list)
    pipeline_ia: AIPipelineResult | None = None
    etapas_ia_executadas: list[str] = Field(default_factory=list)
    etapas_ia_com_fallback: list[str] = Field(default_factory=list)
    evidencias_relevantes_para_vaga: list[SelectedEvidence] = Field(default_factory=list)
    classificacao_vaga_ia: AIJobClassification | None = None
    avaliacao_contextual_requisitos: list[ContextualRequirementEvaluation] = Field(default_factory=list)
    confianca_pipeline_ia: int | None = Field(default=None, ge=0, le=100)
    grupos_requisitos: list[RequirementGroup] = Field(default_factory=list)
    score_por_grupo: dict[str, int] = Field(default_factory=dict)
    score_semantico_agrupado: int | None = Field(default=None, ge=0, le=100)
    erros_pipeline_ia_sanitizados: list[str] = Field(default_factory=list)
    detalhes_fallback_pipeline: list[dict] = Field(default_factory=list)
    parser_warnings: list[str] = Field(default_factory=list)
    secoes_detectadas: list[str] = Field(default_factory=list)
    secoes_com_baixa_confianca: list[str] = Field(default_factory=list)
    fontes_evidencia_resumo: dict[str, int] = Field(default_factory=dict)
    sanitizacao_resumo: dict[str, object] = Field(default_factory=dict)


class AIComplement(BaseModel):
    """reaproveitado por um provedor IA"""

    resumo_gerado: str = Field(min_length=1)

    sugestoes: list[str] = Field(min_length=1)
