from app.schemas.analise import SolicitacaoAnalise
from app.services.analisador_ats import (
    analisar_curriculo,
    detectar_secoes_ausentes,
    extrair_palavras_relevantes,
)


def test_identifica_palavras_encontradas_e_faltantes() -> None:

    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Experiência com Python e APIs REST.",
        vaga_texto="Desenvolvimento Python com FastAPI e Docker.",
    )

    resultado = analisar_curriculo(solicitacao)

    assert "Python" in resultado.palavras_chave_encontradas
    assert "FastAPI" in resultado.palavras_chave_faltando

    assert "Docker" in resultado.palavras_chave_faltando
    assert 0 <= resultado.pontuacao_ats <= 100


def test_rejeita_curriculo_e_vaga_iguais() -> None:

    solicitacao = SolicitacaoAnalise(
        curriculo_texto="Python FastAPI Docker",
        vaga_texto="Python FastAPI Docker",
    )

    resultado = analisar_curriculo(solicitacao)

    assert resultado.analise_valida is False
    assert resultado.pontuacao_ats == 0
    assert resultado.alertas_entrada


def test_detecta_secoes_ausentes() -> None:

    problemas = detectar_secoes_ausentes("Experiência profissional com Python.")

    assert "Seção de experiência não identificada no currículo." not in problemas

    assert "Seção de formação não identificada no currículo." in problemas
    assert "Seção de projetos não identificada no currículo." in problemas


def test_ignora_termos_genericos_da_vaga() -> None:

    palavras = extrair_palavras_relevantes("Qualificações user system React")
    assert "qualificacoes" not in palavras
    assert "user" not in palavras
    assert "system" not in palavras
    assert "React" in palavras


def test_prioriza_palavras_compostas_e_tecnologias() -> None:

    palavras = extrair_palavras_relevantes(
        "Next.js, Tailwind CSS, Radix UI, shadcn/ui e design system"
    )

    assert {"Next.js", "Tailwind CSS", "Radix UI", "shadcn/ui", "design system"} <= set(
        palavras
    )


def test_requisitos_obrigatorios_pesam_mais_que_diferenciais() -> None:

    resultado = analisar_curriculo(
        SolicitacaoAnalise(
            curriculo_texto="React",
            vaga_texto="Requisitos obrigatórios:\nReact\nDiferenciais:\nFigma",
        )
    )

    assert resultado.pontuacao_ats == 56


def test_ignora_metadados_de_agregadores() -> None:

    palavras = extrair_palavras_relevantes(
        "Job description via LinkedIn. Apply on Indeed. Glassdoor. 3 days ago. NestJS"
    )

    assert palavras == ["NestJS"]


def test_extrai_catalogo_tecnico_backend_e_frontend() -> None:

    palavras = extrair_palavras_relevantes(
        "NestJS, AWS-SDK, Angular, Jest, Mocha, MongoDB e DynamoDB"
    )

    assert {
        "NestJS",
        "AWS-SDK",
        "Angular",
        "Jest",
        "Mocha",
        "MongoDB",
        "DynamoDB",
    } <= set(palavras)


def test_detecta_graduacao_completa_contra_cursando() -> None:

    resultado = analisar_curriculo(
        SolicitacaoAnalise(
            curriculo_texto="Formação: graduação em Sistemas, cursando.",
            vaga_texto="Requisitos obrigatórios:\nGraduação completa",
        )
    )

    assert (
        "Vaga pede graduação completa; currículo indica graduação em andamento."
        in resultado.analise_detalhada.possiveis_impeditivos
    )


def test_detecta_ingles_avancado_contra_tecnico() -> None:

    resultado = analisar_curriculo(
        SolicitacaoAnalise(
            curriculo_texto="Idiomas: inglês técnico.",
            vaga_texto="Requisitos obrigatórios:\nInglês avançado",
        )
    )

    assert (
        "Vaga pede inglês avançado; currículo indica inglês técnico."
        in resultado.analise_detalhada.possiveis_impeditivos
    )


def test_detecta_localidade_hibrida_incompativel() -> None:

    resultado = analisar_curriculo(
        SolicitacaoAnalise(
            curriculo_texto="Localização: Recife.",
            vaga_texto="Trabalho híbrido em Manaus. Requisitos: Python.",
        )
    )

    assert (
        "Vaga é híbrida/presencial em Manaus; currículo indica Recife."
        in resultado.analise_detalhada.possiveis_impeditivos
    )
