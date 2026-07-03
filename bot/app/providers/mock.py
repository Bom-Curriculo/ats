from app.providers.base import AIProvider
from app.schemas.analysis import AIComplement, AnalysisResult, AnalysisRequest


class MockProvider(AIProvider):
    nome = "mock"

    def __init__(
        self,
        modelo: str = "modelo-mock",
        resumo: str = "Resumo gerado pelo provedor de teste.",
        sugestoes: list[str] | None = None,
        resposta_estruturada: dict | str | None = None,
        erro_simulado: Exception | None = None,
        respostas_por_tarefa: dict[str, dict | str | Exception] | None = None,
    ) -> None:
        self.modelo = modelo
        self.resumo = resumo
        self.sugestoes = sugestoes or ["Sugestão gerada pelo provedor de teste."]
        self.resposta_estruturada = resposta_estruturada
        self.erro_simulado = erro_simulado
        self.respostas_por_tarefa = respostas_por_tarefa or {}
        self.prompts_tarefas: list[tuple[str, str]] = []

    async def gerar_complemento(
        self,
        solicitacao: AnalysisRequest,
        resultado_base: AnalysisResult,
    ) -> AIComplement:
        return AIComplement(
            resumo_gerado=self.resumo,
            sugestoes=self.sugestoes,
        )

    async def gerar_analise_estruturada(self, solicitacao_segura, resultado_local):
        if self.erro_simulado is not None:
            raise self.erro_simulado
        if self.resposta_estruturada is not None:
            return self.resposta_estruturada
        return await super().gerar_analise_estruturada(
            solicitacao_segura, resultado_local
        )

    async def executar_tarefa_estruturada(self, tarefa, prompt, schema, temperatura=0.1):
        self.prompts_tarefas.append((tarefa, prompt))
        resposta = self.respostas_por_tarefa.get(tarefa)
        if isinstance(resposta, Exception):
            raise resposta
        if resposta is None:
            return None
        if isinstance(resposta, str):
            import json
            resposta = json.loads(resposta)
        return schema.model_validate(resposta).model_dump()
