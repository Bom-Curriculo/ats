from typing import Literal


from pydantic import BaseModel, ConfigDict, Field



# literal pra não deixar passar qualquer string nos status
StatusRequisitoIA = Literal[
    "encontrado_com_evidencia",
    "encontrado_sem_contexto_claro",

    "relacionado_mas_nao_explicito",

    "faltando",
    "nao_avaliado",
    "possivel_impeditivo",

]



ImportanciaRequisitoIA = Literal[
    "obrigatorio", "desejavel", "diferencial", "contextual", "nao_informado"
]



CategoriaRequisitoIA = Literal[
    "habilidade_tecnica",
    "ferramenta",
    "experiencia",
    "formacao",
    "idioma",


    "soft_skill",
    "dominio_de_negocio",
    "certificacao",
    "disponibilidade",
    "localizacao",
    "outro",


]



class AnaliseIARequisito(BaseModel):
    item: str = Field(min_length=1)
    categoria: CategoriaRequisitoIA
    importancia: ImportanciaRequisitoIA
    status: StatusRequisitoIA


    evidencia: str | None = None
    justificativa: str = Field(min_length=1)
    recomendacao: str = Field(min_length=1)
    # n aceita campo extra, se vier quebra
    model_config = ConfigDict(extra="forbid")



class RespostaAnaliseIA(BaseModel):
    resumo_contextual: str = Field(min_length=1)
    requisitos_contextuais: list[AnaliseIARequisito]
    pontos_fortes: list[str]
    lacunas: list[str]
    possiveis_impeditivos: list[str]
    sugestoes_de_melhoria: list[str]
    proximos_passos: list[str]

    # alertas anti alucinação
    alertas_contra_inventar: list[str]

    confianca: int = Field(ge=0, le=100)
    score_sugerido_ia: int | None = Field(default=None, ge=0, le=100)
    justificativa_score_ia: str | None = None

    papel_ia: list[str] = Field(default_factory=list)


    qualidade_contexto_ia: int | None = Field(default=None, ge=0, le=100)


    avaliacao_relevancia: dict | None = None


    matriz_evidencia: list[dict] = Field(default_factory=list)


    lacunas_priorizadas: list[dict] = Field(default_factory=list)
    sugestoes_de_reescrita_seguras: list[str] = Field(default_factory=list)
    diagnostico_ats: dict | None = None
    score_contextual_ia: int | None = Field(default=None, ge=0, le=100)


    model_config = ConfigDict(extra="forbid")
