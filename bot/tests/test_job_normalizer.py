from app.services.job_normalizer import clean_job_text


def test_removes_portais_e_metadados_de_candidatura() -> None:

    # joga coisas do agregador e conferi se saiu tudo
    resultado = clean_job_text(
        "Job description\nApply on Indeed via LinkedIn\n3 days ago\nRequisitos:\nNestJS"
    ).lower()

    for ruido in ("apply", "indeed", "linkedin", "days ago", "job description"):
        assert ruido not in resultado

    assert "nestjs" in resultado


def test_removes_bloco_de_beneficios_ate_proximo_cabecalho() -> None:

    resultado = clean_job_text(
        "Benefícios:\nVale alimentação\nGympass\nRequisitos:\nPython"
    )

    assert "Vale alimentação" not in resultado

    assert "Gympass" not in resultado

    assert "Python" in resultado
