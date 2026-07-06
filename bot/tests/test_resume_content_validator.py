from app.services.parsing.resume_content_validator import ResumeContentValidator

REALISTIC_RESUME_TEXT = (
    "João Silva - Desenvolvedor Backend Júnior\n"
    "COMPETÊNCIAS TÉCNICAS\n"
    "Python, JavaScript, HTML, CSS, Git, SQL, Docker.\n"
    "PROJETOS\n"
    "Sistema de gestão de tarefas usando Python e Flask, com banco de dados "
    "PostgreSQL e testes automatizados.\n"
    "FORMAÇÃO\n"
    "Bacharelado em Ciência da Computação, Universidade Federal, 2023-2026."
)


def test_accepts_realistic_resume_text() -> None:
    result = ResumeContentValidator().validate(REALISTIC_RESUME_TEXT)
    assert result.is_valid is True
    assert result.reason is None


def test_rejects_empty_text() -> None:
    result = ResumeContentValidator().validate("")
    assert result.is_valid is False
    assert result.reason == "empty"


def test_rejects_whitespace_only_text() -> None:
    result = ResumeContentValidator().validate("   \n\n  ")
    assert result.is_valid is False
    assert result.reason == "empty"


def test_rejects_too_short_text() -> None:
    result = ResumeContentValidator().validate("Meu nome é João e sou desenvolvedor.")
    assert result.is_valid is False
    assert result.reason == "too_short"


def test_rejects_repeated_troll_content() -> None:
    troll_text = "teste " * 40
    result = ResumeContentValidator().validate(troll_text)
    assert result.is_valid is False
    assert result.reason == "low_content_diversity"


def test_rejects_long_gibberish() -> None:
    gibberish = " ".join(["asdkjasd"] * 40)
    result = ResumeContentValidator().validate(gibberish)
    assert result.is_valid is False
    assert result.reason == "low_content_diversity"
