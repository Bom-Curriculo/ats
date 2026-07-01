from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.analise_ia import AnaliseIARequisito, RespostaAnaliseIA
from app.schemas.pipeline_ia import (
    AvaliacaoContextualRequisito,
    ClassificacaoVagaIA,
    EvidenciaSelecionada,
    ResultadoPipelineIA,
)


TipoFonteCurriculo = Literal["curriculo_texto", "curriculo_pdf", "linkedin_pdf", "linkedin_text",
    "linkedin_url", "github_url", "portfolio_url", "portfolio_text", "vaga_texto", "vaga_url",
    "informacoes_pessoais", "instrucoes_customizadas"]


class FonteCurriculo(BaseModel):
    tipo: TipoFonteCurriculo
    conteudo: str | None = None
    url: str | None = None


class SolicitacaoAnalise(BaseModel):
    curriculo_texto: str = Field(default="", description="Texto completo do currículo")

    vaga_texto: str = Field(min_length=1, description="Descrição completa da vaga")

    idioma: str = Field(default="pt-BR", min_length=2)

    # Mapenas pra compatibilidade
    usar_ia: bool | None = None

    nivel_vaga: str | None = None
    fontes_curriculo: list[FonteCurriculo] = Field(default_factory=list)

    @model_validator(mode="after")
    def consolidar_fontes_textuais(self):
        if not self.curriculo_texto.strip():
            tipos_textuais = {"curriculo_texto", "linkedin_text", "portfolio_text", "informacoes_pessoais", "instrucoes_customizadas"}
            textos = [fonte.conteudo.strip() for fonte in self.fontes_curriculo
                      if fonte.tipo in tipos_textuais and fonte.conteudo and fonte.conteudo.strip()]
            if not textos:
                raise ValueError("curriculo_texto ou uma fonte textual de currículo é obrigatório")
            self.curriculo_texto = "\n\n".join(textos)
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "curriculo_texto": "texto do currículo",
                "vaga_texto": "texto da vaga",
                "idioma": "pt-BR",
            }
        }
    )


class InformacoesPrivacidade(BaseModel):
    """Metadados seguros sobre o tratamento anterior à chamada de IA."""

    dados_sensiveis_detectados: bool = False

    itens_removidos_antes_ia: list[str] = Field(default_factory=list)

    texto_enviado_para_ia_foi_sanitizado: bool = False


class AnaliseDetalhada(BaseModel):
    """Classificação das correspondências pra vaga"""

    requisitos_obrigatorios_encontrados: list[str] = Field(default_factory=list)

    requisitos_obrigatorios_faltando: list[str] = Field(default_factory=list)

    diferenciais_encontrados: list[str] = Field(default_factory=list)

    diferenciais_faltando: list[str] = Field(default_factory=list)

    tecnologias_encontradas: list[str] = Field(default_factory=list)

    tecnologias_faltando: list[str] = Field(default_factory=list)

    possiveis_impeditivos: list[str] = Field(default_factory=list)


class SugestoesDetalhadas(BaseModel):
    """separa sem pressupor experiência."""

    ajustes_recomendados: list[str] = Field(default_factory=list)

    lacunas_tecnicas: list[str] = Field(default_factory=list)

    pontos_de_atencao: list[str] = Field(default_factory=list)

    proximos_passos: list[str] = Field(default_factory=list)

    ajustes_no_curriculo: list[str] = Field(default_factory=list)
    lacunas_reais: list[str] = Field(default_factory=list)
    proximos_passos_de_estudo: list[str] = Field(default_factory=list)
    alertas_contra_inventar: list[str] = Field(default_factory=list)


class ItemAnaliseRequisito(BaseModel):
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


class EvidenciasCurriculo(BaseModel):
    experiencia_profissional: bool = False

    projetos_pessoais: bool = False

    projetos_academicos: bool = False

    open_source: bool = False

    cursos: bool = False

    residencia_tecnologica: bool = False

    secao_habilidades: bool = False


class FallbackIA(BaseModel):
    """tentativas de provedores"""

    fallback_usado: bool = False

    provedores_tentados: list[str] = Field(default_factory=list)

    provedores_ignorados_por_configuracao: list[str] = Field(default_factory=list)

    ultimo_erro_sanitizado: str | None = None

    erros_provedores_sanitizados: list[str] = Field(default_factory=list)


class ErroProviderSanitizado(BaseModel):
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


class GrupoRequisito(BaseModel):
    nome: str
    tipo: str
    modo: str
    itens: list[str] = Field(default_factory=list)
    status_grupo: str
    evidencia_resumida: str | None = None
    impacto_score: float = 0
    justificativa: str | None = None


class ResultadoAnalise(BaseModel):
    """resu8ltado que é consumido"""

    pontuacao_ats: int = Field(ge=0, le=100)

    palavras_chave_encontradas: list[str]

    palavras_chave_faltando: list[str]

    problemas_detectados: list[str]

    sugestoes: list[str]

    resumo_gerado: str

    provedor_ia: str = "sem_ia"

    modelo_ia: str | None = None

    privacidade: InformacoesPrivacidade | None = None

    analise_detalhada: AnaliseDetalhada | None = None

    sugestoes_detalhadas: SugestoesDetalhadas | None = None

    analise_valida: bool = True

    alertas_entrada: list[str] = Field(default_factory=list)

    inventario_curriculo: dict[str, list[str]] | None = None

    analise_por_requisito: list[ItemAnaliseRequisito] = Field(default_factory=list)

    evidencias: EvidenciasCurriculo | None = None

    explicacao_matching: str = ""

    fallback_ia: FallbackIA | None = None

    analise_ia: RespostaAnaliseIA | None = None
    score_sugerido_ia: int | None = Field(default=None, ge=0, le=100)
    justificativa_score_ia: str | None = None
    confianca_ia: int | None = Field(default=None, ge=0, le=100)
    fallback_local_usado: bool = False
    requisitos_contextuais: list[AnaliseIARequisito] = Field(default_factory=list)
    lacunas_contextuais: list[str] = Field(default_factory=list)
    proximos_passos: list[str] = Field(default_factory=list)
    alertas_contra_inventar: list[str] = Field(default_factory=list)
    provedores_tentados: list[str] = Field(default_factory=list)
    erros_provedores_sanitizados: list[str] = Field(default_factory=list)
    detalhes_erros_provedores: list[ErroProviderSanitizado] = Field(default_factory=list)
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
    pipeline_ia: ResultadoPipelineIA | None = None
    etapas_ia_executadas: list[str] = Field(default_factory=list)
    etapas_ia_com_fallback: list[str] = Field(default_factory=list)
    evidencias_relevantes_para_vaga: list[EvidenciaSelecionada] = Field(default_factory=list)
    classificacao_vaga_ia: ClassificacaoVagaIA | None = None
    avaliacao_contextual_requisitos: list[AvaliacaoContextualRequisito] = Field(default_factory=list)
    confianca_pipeline_ia: int | None = Field(default=None, ge=0, le=100)
    grupos_requisitos: list[GrupoRequisito] = Field(default_factory=list)
    score_por_grupo: dict[str, int] = Field(default_factory=dict)
    score_semantico_agrupado: int | None = Field(default=None, ge=0, le=100)
    erros_pipeline_ia_sanitizados: list[str] = Field(default_factory=list)
    detalhes_fallback_pipeline: list[dict] = Field(default_factory=list)
    parser_warnings: list[str] = Field(default_factory=list)
    secoes_detectadas: list[str] = Field(default_factory=list)
    secoes_com_baixa_confianca: list[str] = Field(default_factory=list)
    fontes_evidencia_resumo: dict[str, int] = Field(default_factory=dict)
    sanitizacao_resumo: dict[str, object] = Field(default_factory=dict)


class ComplementoIA(BaseModel):
    """reaproveitado por um provedor IA"""

    resumo_gerado: str = Field(min_length=1)

    sugestoes: list[str] = Field(min_length=1)
