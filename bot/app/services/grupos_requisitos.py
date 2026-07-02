
import re

from app.schemas.analise import GrupoRequisito, ItemAnaliseRequisito
from app.services.equivalencias_tecnicas import NivelEvidencia, NivelVaga, peso_fonte
from app.services.catalogo_tecnologias import CATALOGO
from app.services.matching_tecnico import contem_alias
from app.services.normalizador_texto import normalizar_para_comparacao


# grupos de subrequisitos conhecidos
SQL = {"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}
GIT = {"Git", "branches", "pull requests", "code review"}
IA = {"LLMs", "APIs de IA", "Prompt Engineering"}


def _valor(item: ItemAnaliseRequisito | None, nivel: NivelVaga) -> float:
    if not item:
        return 0
    return peso_fonte(nivel, NivelEvidencia(item.nivel_evidencia))


def _status(valor: float) -> str:
    return "atendido" if valor >= .75 else ("parcialmente_atendido" if valor > 0 else "nao_atendido")


def _fonte(itens: list[ItemAnaliseRequisito]) -> str | None:
    fontes = list(dict.fromkeys(x.fonte_evidencia for x in itens if x.fonte_evidencia))
    return "; ".join(fontes) if fontes else None


# acha "X ou Y" explicito na descricao da vaga
def _alternativas_explicitas(vaga: str, disponiveis: set[str]) -> list[list[str]]:

    grupos = []

    for linha in vaga.splitlines():
        partes = re.split(r"\s+(?:ou|or)\s+", normalizar_para_comparacao(linha))
        if len(partes) < 2:
            continue
        encontrados = []

        for parte in partes:
            candidatos = [t.nome for t in CATALOGO if t.nome in disponiveis and contem_alias(parte, t.aliases, t.nome)]
            if candidatos:
                encontrados.append(candidatos[-1])

        encontrados = list(dict.fromkeys(encontrados))

        if len(encontrados) >= 2:
            grupos.append(encontrados)
    return grupos


def construir_grupos_requisitos(itens: list[ItemAnaliseRequisito], nivel_texto: str, vaga_texto: str = "") -> tuple[list[GrupoRequisito], int, dict[str, int]]:
    try:
        nivel = NivelVaga(nivel_texto)


    except ValueError:
        nivel = NivelVaga.NAO_INFORMADO
    mapa = {x.item: x for x in itens}

    grupos: list[GrupoRequisito] = []
    usados: set[str] = set()

    def adicionar(nome: str, nomes: list[str], modo: str, tipo: str, valor: float):


        existentes = [mapa[n] for n in nomes if n in mapa]
        if not existentes:


            return
        usados.update(x.item for x in existentes)
        grupos.append(GrupoRequisito(nome=nome, tipo=tipo, modo=modo,
            itens=[x.item for x in existentes], status_grupo=_status(valor),

            evidencia_resumida=_fonte(existentes), impacto_score=round(valor * 100, 1),

            justificativa=("Uma alternativa comprovada atende o grupo." if modo == "any" else
                           "Itens complementares são ponderados sem multiplicar penalidades." if modo == "weighted" else
                           "Todos os itens do grupo contribuem para o atendimento.")))



    for alternativas in _alternativas_explicitas(vaga_texto, set(mapa)):
        # Ramos de framework Python já são avaliados dentro do grupo backend composto.
        if set(alternativas) <= {"FastAPI", "Flask", "Django"}:
            continue
        tipo_alternativa = "diferencial" if all(mapa[x].categoria == "diferencial" for x in alternativas) else "obrigatorio"
        adicionar("Alternativas: " + " ou ".join(alternativas), alternativas, "any", tipo_alternativa,
                  max(_valor(mapa[x], nivel) for x in alternativas))



    # Stacks de front-end são alternativas válidas no matching, mesmo quando listadas lado a lado.
    front = [x for x in ("Angular", "React") if x in mapa and x not in usados]
    adicionar("Stack front-end", front, "any", "obrigatorio",
              max((_valor(mapa[x], nivel) for x in front), default=0))

    java = [_valor(mapa.get(x), nivel) for x in ("Java", "Spring Boot") if x in mapa]
    python = [_valor(mapa.get(x), nivel) for x in ("Python", "FastAPI", "Flask") if x in mapa]
    backend_nomes = [x for x in ("Java", "Spring Boot", "Python", "FastAPI", "Flask") if x in mapa]


    if backend_nomes:
        ramo_java = sum(java) / len(java) if java else 0
        # FastAPI/Flask são alternativas; Python + melhor framework compõem o ramo.
        linguagem = _valor(mapa.get("Python"), nivel)
        framework = max(_valor(mapa.get("FastAPI"), nivel), _valor(mapa.get("Flask"), nivel))
        ramo_python = (linguagem + framework) / 2 if linguagem or framework else 0
        adicionar("Backend Java ou Python", backend_nomes, "any", "obrigatorio", max(ramo_java, ramo_python))



    sql_itens = [x for x in SQL if x in mapa]
    if sql_itens:
        base = _valor(mapa.get("SQL"), nivel)
        comandos = [_valor(mapa[x], nivel) for x in sql_itens if x != "SQL"]
        valor = base * .7 + (max(comandos) if comandos else base) * .3
        adicionar("SQL e operações CRUD", sorted(sql_itens, key=lambda x: (x != "SQL", x)), "weighted", "obrigatorio", valor)



    devops = [x for x in ("Docker", "Kubernetes") if x in mapa]
    adicionar("Contêineres e orquestração", devops, "all", "obrigatorio",
              sum(_valor(mapa[x], nivel) for x in devops) / len(devops) if devops else 0)



    git = [x for x in GIT if x in mapa]
    adicionar("Git e fluxo colaborativo", git, "weighted", "obrigatorio",
              sum(_valor(mapa[x], nivel) for x in git) / len(git) if git else 0)

    ia = [x for x in IA if x in mapa]
    adicionar("Experiência com IA", ia, "weighted", "diferencial",
              sum(_valor(mapa[x], nivel) for x in ia) / len(ia) if ia else 0)

    # itens q não entraram em nenhum grupo
    for item in itens:
        if item.item in usados:
            continue
        tipo = "diferencial" if item.categoria == "diferencial" else ("contexto" if item.categoria == "contexto" else "obrigatorio")
        adicionar(item.item, [item.item], "all", tipo, _valor(item, nivel))


    pesos = {"obrigatorio": 3.0, "desejavel": 2.0, "diferencial": 1.0, "contexto": .5}
    total = sum(pesos.get(g.tipo, 1) for g in grupos)
    pontos = sum(pesos.get(g.tipo, 1) * g.impacto_score / 100 for g in grupos)
    score = round(pontos / total * 100) if total else 0
    return grupos, score, {g.nome: round(g.impacto_score) for g in grupos}
