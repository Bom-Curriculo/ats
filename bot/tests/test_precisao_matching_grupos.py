from app.schemas.analise import SolicitacaoAnalise
from app.services.analisador_ats import analisar_curriculo


def analisar(cv: str, vaga: str):
    return analisar_curriculo(SolicitacaoAnalise(curriculo_texto=cv, vaga_texto=vaga, nivel_vaga="junior"))


def item(resultado, nome):
    return next(x for x in resultado.analise_por_requisito if x.item == nome)


def test_limites_tecnicos_java_rag_e_apis():
    java = analisar("PROJETOS\nJavaScript", "Requisitos:\nJava")
    rag = analisar("PROJETOS\nInterface com drag and drop", "Diferenciais:\nRAG")
    ia = analisar("PROJETOS\nAPI REST em FastAPI", "Diferenciais:\nAPIs de IA")
    assert item(java, "Java").status == "faltando"
    assert item(rag, "RAG").status == "faltando"
    assert item(ia, "APIs de IA").status == "faltando"


def test_typescript_relaciona_javascript_apenas_no_sentido_correto():
    ts = analisar("PROJETOS\nTypeScript", "Requisitos:\nJavaScript")
    js = analisar("PROJETOS\nJavaScript", "Requisitos:\nTypeScript")
    assert item(ts, "JavaScript").status == "relacionado_mas_nao_explicito"
    assert item(js, "TypeScript").status == "faltando"


def test_fonte_pratica_vence_curso_para_docker_python_sql():
    resultado = analisar(
        "PROJETOS\nAPI Python com SQL executada em Docker\nCURSOS\nPython, SQL e Docker",
        "Requisitos:\nPython, SQL e Docker",
    )
    for nome in ("Docker", "Python", "SQL"):
        assert item(resultado, nome).fonte_evidencia == "projeto"
        assert item(resultado, nome).nivel_evidencia == "evidencia_pratica_forte"


def test_curso_e_skill_nao_viram_pratica():
    resultado = analisar("CURSOS\nSpring Boot e Java\nCOMPETÊNCIAS\nSpring Boot, Java", "Requisitos:\nSpring Boot e Java")
    assert item(resultado, "Spring Boot").nivel_evidencia == "evidencia_educacional"
    assert item(resultado, "Java").nivel_evidencia == "evidencia_educacional"


def test_grupos_alternativos_e_sql_crud():
    resultado = analisar(
        "PROJETOS\nReact, Python, FastAPI e SQL com SELECT em Docker",
        "Front-end:\nAngular e React\nBack-end:\nJava com Spring Boot ou Python com FastAPI ou Flask\nBanco de dados:\nSQL, SELECT, JOIN, WHERE, INSERT, UPDATE e DELETE",
    )
    grupos = {x.nome: x for x in resultado.grupos_requisitos}
    assert grupos["Stack front-end"].modo == "any"
    assert grupos["Stack front-end"].status_grupo == "atendido"
    assert grupos["Backend Java ou Python"].status_grupo == "atendido"
    assert grupos["SQL e operações CRUD"].modo == "weighted"
    assert set(grupos["SQL e operações CRUD"].itens) >= {"SQL", "SELECT", "JOIN"}


def test_getronics_headings_geram_centrais_e_diferenciais_separados():
    vaga = """Desenvolvedor Full Stack - Getronics
Front-end:
Angular e React
HTML5, CSS3, JavaScript e TypeScript
Back-end:
Java com Spring Boot
Python com FastAPI ou Flask
Banco de dados:
SQL, SELECT, JOIN, WHERE, INSERT, UPDATE e DELETE
DevOps:
Docker e Kubernetes
Versionamento:
Git, branches, pull requests e code review
Diferenciais:
Testes unitários, testes de integração, metodologias ágeis, inglês técnico, LLMs, APIs de IA e Prompt Engineering
"""
    resultado = analisar("PROJETOS\nReact, Python, FastAPI, SQL e Docker", vaga)
    assert any(x.peso >= 2 for x in resultado.analise_por_requisito)
    diferenciais = {x.item for x in resultado.analise_por_requisito if x.categoria == "diferencial"}
    assert {"testes unitários", "metodologias ágeis", "inglês técnico", "LLMs", "APIs de IA", "Prompt Engineering"} <= diferenciais
    assert resultado.score_semantico_agrupado == resultado.pontuacao_ats
