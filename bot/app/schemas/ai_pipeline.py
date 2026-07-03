from pydantic import BaseModel, ConfigDict, Field



class AIJobClassification(BaseModel):
    titulo: str | None = None
    senioridade: str | None = None
    area: str | None = None
    requisitos_centrais: list[str] = Field(default_factory=list)
    requisitos_secundarios: list[str] = Field(default_factory=list)
    diferenciais: list[str] = Field(default_factory=list)


    # sem hard filters
    hard_filters: list[str] = Field(default_factory=list)
    contexto_negocio: list[str] = Field(default_factory=list)
    confianca: int | None = Field(default=None, ge=0, le=100)
    empresa: str | None = None
    tecnologias: list[str] = Field(default_factory=list)


    responsabilidades: list[str] = Field(default_factory=list)


    modalidade: str | None = None
    localizacao: str | None = None


    # se a vaga aceita junior sem exp
    aceita_sem_experiencia: bool = False


    # ignora campo extra q vier da ia
    model_config = ConfigDict(extra="ignore")



class SelectedEvidence(BaseModel):
    item: str
    fonte: str | None = None


    tipo_fonte: str | None = None
    trecho: str | None = None


    # nivel da evidencia: direta, indireta, inferida...
    nivel_evidencia: str = "sem_evidencia"
    confianca: int | None = Field(default=None, ge=0, le=100)
    relacionado_a: list[str] = Field(default_factory=list)



class ContextualRequirementEvaluation(BaseModel):
    item: str
    importancia: str = "nao_informado"
    relevancia_para_vaga: str = "media"
    status: str = "nao_avaliado"
    evidencia_usada: SelectedEvidence | None = None

    # true se o cara realmente nao tem a skill
    lacuna_real: bool = False

    # true se pode ser so falta de descricao no curriculo
    lacuna_de_descricao: bool = False
    recomendacao_segura: str = ""
    # chance da ia ter alucinado nesse item
    risco_alucinacao: str = "baixo"
    model_config = ConfigDict(extra="ignore")



class AIPipelineResult(BaseModel):
    classificacao_vaga: AIJobClassification | None = None
    evidencias_relevantes: list[SelectedEvidence] = Field(default_factory=list)
    avaliacao_requisitos: list[ContextualRequirementEvaluation] = Field(default_factory=list)
    lacunas_priorizadas: list[dict] = Field(default_factory=list)


    sugestoes_seguras: list[str] = Field(default_factory=list)
    score_contextual_ia: int | None = Field(default=None, ge=0, le=100)
    confianca_pipeline: int | None = Field(default=None, ge=0, le=100)


    # quais etapas rodaram com sucesso
    etapas_executadas: list[str] = Field(default_factory=list)


    # quais etapas cairam no fallback
    etapas_com_fallback: list[str] = Field(default_factory=list)


    detalhes_fallback: list[dict] = Field(default_factory=list)
