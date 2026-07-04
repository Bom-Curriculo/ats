from app.schemas.analysis import AnalysisRequest
from app.services.ats_analyzer import analyze_resume


def analyze(cv: str, job: str):
    return analyze_resume(AnalysisRequest(resume_text=cv, job_text=job, job_level="junior"))


def item(result, name):
    return next(x for x in result.requirement_analysis if x.item == name)


def test_matching_group_accuracy_behavior_01():
    java = analyze("PROJETOS\nJavaScript", "Requisitos:\nJava")
    rag = analyze("PROJETOS\nInterface com drag and drop", "Diferenciais:\nRAG")
    ia = analyze("PROJETOS\nAPI REST em FastAPI", "Diferenciais:\nAPIs de IA")
    assert item(java, "Java").status == "missing"
    assert item(rag, "RAG").status == "missing"
    assert item(ia, "APIs de IA").status == "missing"


def test_matching_group_accuracy_behavior_02():
    ts = analyze("PROJETOS\nTypeScript", "Requisitos:\nJavaScript")
    js = analyze("PROJETOS\nJavaScript", "Requisitos:\nTypeScript")
    assert item(ts, "JavaScript").status == "related_but_not_explicit"
    assert item(js, "TypeScript").status == "missing"


def test_matching_group_accuracy_behavior_03():
    result = analyze(
        "PROJETOS\nAPI Python com SQL executada em Docker\nCURSOS\nPython, SQL e Docker",
        "Requisitos:\nPython, SQL e Docker",
    )
    for name in ("Docker", "Python", "SQL"):
        assert item(result, name).evidence_source == "project"
        assert item(result, name).evidence_level == "strong_practical_evidence"


def test_matching_group_accuracy_behavior_04():
    result = analyze("CURSOS\nSpring Boot e Java\nCOMPETÊNCIAS\nSpring Boot, Java", "Requisitos:\nSpring Boot e Java")
    assert item(result, "Spring Boot").evidence_level == "educational_evidence"
    assert item(result, "Java").evidence_level == "educational_evidence"


def test_matching_group_accuracy_behavior_05():
    result = analyze(
        "PROJETOS\nReact, Python, FastAPI e SQL com SELECT em Docker",
        "Front-end:\nAngular e React\nBack-end:\nJava com Spring Boot ou Python com FastAPI ou Flask\nBanco de dados:\nSQL, SELECT, JOIN, WHERE, INSERT, UPDATE e DELETE",
    )
    grupos = {x.name: x for x in result.requirement_groups}
    assert grupos["Stack front-end"].mode == "any"
    assert grupos["Stack front-end"].group_status == "atendido"
    assert grupos["Backend Java ou Python"].group_status == "atendido"
    assert grupos["SQL e operações CRUD"].mode == "weighted"
    assert set(grupos["SQL e operações CRUD"].items) >= {"SQL", "SELECT", "JOIN"}


def test_matching_group_accuracy_behavior_06():
    job = """Desenvolvedor Full Stack - Getronics
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
    result = analyze("PROJETOS\nReact, Python, FastAPI, SQL e Docker", job)
    assert any(x.weight >= 2 for x in result.requirement_analysis)
    differentials = {x.item for x in result.requirement_analysis if x.category == "differential"}
    assert {"testes unitários", "metodologias ágeis", "inglês técnico", "LLMs", "APIs de IA", "Prompt Engineering"} <= differentials
    assert result.grouped_semantic_score == result.ats_score
