from app.services.normalizador_vaga import limpar_texto_vaga


def test_remove_portais_e_metadados_de_candidatura() -> None:

    # joga coisas do agregador e conferi se saiu tudo
    resultado = limpar_texto_vaga(
        "Job description\nApply on Indeed via LinkedIn\n3 days ago\nRequisitos:\nNestJS"
    ).lower()

    for ruido in ("apply", "indeed", "linkedin", "days ago", "job description"):
        assert ruido not in resultado

    assert "nestjs" in resultado


def test_remove_bloco_de_beneficios_ate_proximo_cabecalho() -> None:

    resultado = limpar_texto_vaga(
        "Benefícios:\nVale alimentação\nGympass\nRequisitos:\nPython"
    )

    assert "Vale alimentação" not in resultado

    assert "Gympass" not in resultado

    assert "Python" in resultado
