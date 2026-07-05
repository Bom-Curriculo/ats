from app.services.normalization.job_normalizer import clean_job_text


def test_job_normalizer_behavior_01() -> None:

    # Implementation note.
    result = clean_job_text(
        "Job description\nApply on Indeed via LinkedIn\n3 days ago\nRequisitos:\nNestJS"
    ).lower()

    for ruido in ("apply", "indeed", "linkedin", "days ago", "job description"):
        assert ruido not in result

    assert "nestjs" in result


def test_job_normalizer_behavior_02() -> None:

    result = clean_job_text(
        "Benefícios:\nVale alimentação\nGympass\nRequisitos:\nPython"
    )

    assert "Vale alimentação" not in result

    assert "Gympass" not in result

    assert "Python" in result
