"""Testes do inventário, evidências e comportamento para início de carreira."""

from app.schemas.analise import SolicitacaoAnalise
from app.services.analisador_ats import analisar_curriculo
from app.services.extrator_secoes import extrair_secoes_curriculo
from app.services.catalogo_tecnologias import Tecnologia
from app.services.inventario_curriculo import extrair_inventario_curriculo


# evita REPETINDOANALISE ficar repetindo
def analisar(curriculo: str, vaga: str):

    return analisar_curriculo(
        SolicitacaoAnalise(curriculo_texto=curriculo, vaga_texto=vaga)
    )


def test_inventario_lista_habilidades_nao_exigidas() -> None:

    resultado = analisar(
        "COMPETÊNCIAS TÉCNICAS\nJava, CSharp, DotNet, Python",
        "Requisitos:\nPython",
    )

    # ve se as linguagens foram pegas do catalogo
    assert {"Java", "C#"} <= set(resultado.inventario_curriculo["linguagens"])

    assert ".NET" in resultado.inventario_curriculo["backend"]

    # so python era exigido, ent é aqui
    assert {"Java", "C#", ".NET"} <= set(
        resultado.inventario_curriculo["habilidades_nao_exigidas_pela_vaga"]
    )

    assert resultado.palavras_chave_encontradas == ["Python"]


def test_alias_express_satisfaz_expressjs() -> None:

    resultado = analisar(
        "PROJETOS\nAPI construída com Node.js & Express.",
        "Requisitos:\nExpress.js",
    )

    # express do express.js: evidência
    item = next(i for i in resultado.analise_por_requisito if i.item == "Express.js")

    assert item.status == "encontrado_com_evidencia"


def test_github_actions_e_relacionado_mas_nao_satisfaz_git() -> None:

    resultado = analisar("COMPETÊNCIAS\nGitHub Actions", "Requisitos:\nGit")

    # a lógica é: github actions não implica em pleno conhecimento de Git puro, e vice versa
    item = next(i for i in resultado.analise_por_requisito if i.item == "Git")

    assert item.status == "relacionado_mas_nao_explicito"

    assert "Git" in resultado.palavras_chave_faltando


def test_sem_experiencia_recomenda_projetos_sem_reprovar() -> None:

    resultado = analisar("COMPETÊNCIAS\nPython", "Requisitos:\nPython e FastAPI")

    # mesmo sem experiência a análise tem que se válida
    assert resultado.analise_valida is True

    assert resultado.evidencias.experiencia_profissional is False

    # sugestão projetos pessoais
    assert any(
        "projetos pessoais" in texto
        for texto in resultado.sugestoes_detalhadas.proximos_passos
    )

    # open source sempre escuteri que é muito relevante, ent coloquei isso aqui, pra não pesar muito a falta
    assert not any(
        "open source" in problema.lower() for problema in resultado.problemas_detectados
    )


def test_sem_secao_habilidades_gera_recomendacao_forte() -> None:

    resultado = analisar("PROJETOS\nAPI com Python", "Requisitos:\nPython")

    # recomendar seção habilidades
    assert resultado.evidencias.secao_habilidades is False

    assert any(
        "fortemente recomendada" in texto
        for texto in resultado.sugestoes_detalhadas.ajustes_recomendados
    )


def test_extrai_titulos_de_pdf_espacados() -> None:

    secoes = extrair_secoes_curriculo(
        "C O M P E T Ê N C I A S\nPython\nP R O J E T O S\nAPI"
    )

    assert secoes["competencias_tecnicas"] == "Python"

    assert secoes["projetos"] == "API"


def test_vaga_getronics_extrai_stack_e_praticas_completas() -> None:
    vaga = """Getronics — Pessoa Desenvolvedora
Requisitos: Angular, React, HTML5, CSS3, JavaScript, TypeScript, APIs REST, Java e Spring Boot, Python com FastAPI ou Flask, MVC, integração de sistemas, tratamento de erros, SQL, SELECT, JOIN, WHERE, INSERT, UPDATE, DELETE e modelagem de banco de dados.
Desejáveis: Kubernetes, Docker, CI/CD, Git, branches, pull requests, code review, testes unitários, testes de integração, metodologias ágeis, inglês técnico, LLMs, APIs de IA e Prompt Engineering.
"""
    curriculo = """HABILIDADES
React, TypeScript, JavaScript, Python, FastAPI, SQL, Docker, Git e testes automatizados.
PROJETOS
API REST com Python, FastAPI, SQL, Docker, Git e testes automatizados.
"""

    resultado = analisar(curriculo, vaga)
    requisitos = {item.item for item in resultado.analise_por_requisito}

    assert len(requisitos) >= 30
    assert {
        "React", "TypeScript", "JavaScript", "Python", "FastAPI",
        "SQL", "Docker", "Git", "testes unitários",
    } <= requisitos
    assert {"Angular", "Spring Boot", "Kubernetes", "metodologias ágeis"} <= set(
        resultado.palavras_chave_faltando
    )
    assert not {
        "React", "TypeScript", "JavaScript", "Python", "FastAPI", "SQL", "Docker"
    } & set(resultado.inventario_curriculo["habilidades_nao_exigidas_pela_vaga"])


def test_score_cauteloso_quando_vaga_longa_extrai_um_requisito() -> None:
    vaga = "Requisitos:\nPython\n" + ("Descrição institucional sem competência técnica. " * 10)

    resultado = analisar("HABILIDADES\nPython", vaga)

    assert resultado.pontuacao_ats <= 60
    assert any("Poucos requisitos extraídos" in alerta for alerta in resultado.alertas_entrada)
    assert any("Poucos requisitos extraídos" in problema for problema in resultado.problemas_detectados)


def test_inventario_suporta_processos_e_preserva_contrato() -> None:
    inventario = extrair_inventario_curriculo(
        "HABILIDADES\nMetodologias ágeis, Python e LLMs"
    )
    chaves_antigas = {
        "linguagens", "frontend", "backend", "mobile", "bancos_dados",
        "devops", "cloud", "testes", "ferramentas", "metodologias",
        "idiomas", "formacao", "projetos_detectados", "habilidades_detectadas",
        "habilidades_nao_exigidas_pela_vaga",
    }

    assert "metodologias ágeis" in inventario["processos"]
    assert "LLMs" in inventario["ia"]
    assert {"metodologias ágeis", "Python", "LLMs"} <= set(
        inventario["habilidades_detectadas"]
    )
    assert chaves_antigas <= inventario.keys()


def test_categoria_desconhecida_e_criada_dinamicamente(monkeypatch) -> None:
    import app.services.inventario_curriculo as modulo_inventario

    desconhecida = Tecnologia("Competência futura", "categoria_futura", ("futuro",))
    monkeypatch.setattr(
        modulo_inventario, "CATALOGO", modulo_inventario.CATALOGO + (desconhecida,)
    )

    inventario = modulo_inventario.extrair_inventario_curriculo("Projeto futuro")

    assert inventario["categoria_futura"] == ["Competência futura"]
    assert "Competência futura" in inventario["habilidades_detectadas"]
