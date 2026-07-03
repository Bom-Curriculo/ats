
import json

"""eles são separados por responsabilidades e não incluem fact bank compelto"""

REGRAS = (
    "Retorne somente JSON. Não invente fatos. Curso não é experiência prática. "
    "Skill isolada não comprova prática. Projeto não é emprego. Dados ausentes são lacunas."
)


def prompt_classificacao_vaga(vaga_resumida: str, contexto_local: dict, schema: dict) -> str:
    dados = {"vaga": vaga_resumida[:1800], "sinais_locais": contexto_local}
    return f"Classifique esta vaga: título, senioridade, área, requisitos centrais/secundários, diferenciais, hard filters e contexto de negócio. {REGRAS} Use exatamente este JSON Schema: {json.dumps(schema, ensure_ascii=False)} Dados: {json.dumps(dados, ensure_ascii=False)}"


def prompt_avaliacao_contextual(classificacao: dict, requisitos: list[dict], evidencias: list[dict], schema: dict) -> str:
    dados = {"classificacao": classificacao, "requisitos": requisitos[:30], "evidencias_selecionadas": evidencias[:20]}
    return f"Avalie cada requisito apenas com as evidências fornecidas. Separe lacuna real de falta de descrição e indique risco de alucinação. {REGRAS} Use exatamente este JSON Schema: {json.dumps(schema, ensure_ascii=False)} Dados: {json.dumps(dados, ensure_ascii=False)}"


def prompt_sugestoes_seguras(avaliacoes: list[dict], lacunas: list[dict], schema: dict) -> str:
    dados = {"avaliacoes": avaliacoes[:30], "lacunas_priorizadas": lacunas[:20]}
    return f"Gere sugestões curtas e honestas. Se não houver evidência, recomende estudo ou projeto real; nunca inclusão como experiência. {REGRAS} Use exatamente este JSON Schema: {json.dumps(schema, ensure_ascii=False)} Dados: {json.dumps(dados, ensure_ascii=False)}"
