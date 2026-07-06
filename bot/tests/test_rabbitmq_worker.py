import pytest

from app.models.resume_analysis import ResumeAnalysisResult
from app.services.parsing.resume_content_validator import ResumeContentValidator
from app.workers.rabbitmq_worker import RabbitMQWorker

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


class FakeResumeAnalysisManager:
    def __init__(self) -> None:
        self.received_resume_texts: list[str] = []

    async def extract_resume(self, resume_text: str) -> ResumeAnalysisResult:
        self.received_resume_texts.append(resume_text)
        return ResumeAnalysisResult(score=42, suggestion="Adicione métricas de impacto.")


class FakeResumeFileFetcher:
    def __init__(self, text: str | None = None, error: Exception | None = None) -> None:
        self._text = text
        self._error = error
        self.requested_urls: list[str] = []

    async def fetch_and_extract_text(self, url: str) -> str:
        self.requested_urls.append(url)
        if self._error is not None:
            raise self._error
        return self._text


@pytest.fixture
def worker_factory():
    def _factory(resume_analysis_manager, resume_file_fetcher):
        worker = RabbitMQWorker.__new__(RabbitMQWorker)
        worker._resume_analysis_manager = resume_analysis_manager
        worker._resume_file_fetcher = resume_file_fetcher
        worker._resume_content_validator = ResumeContentValidator()
        return worker

    return _factory


def test_process_payload_with_inline_text_completes(worker_factory):
    manager = FakeResumeAnalysisManager()
    worker = worker_factory(manager, FakeResumeFileFetcher())

    response = worker.process_payload(
        {"resume_text": REALISTIC_RESUME_TEXT, "analysis_request_id": "abc", "user_id": 12}
    )

    assert response.status == "completed"
    assert response.result["score"] == 42
    assert response.result["suggestion"] == "Adicione métricas de impacto."
    assert response.user_id == 12
    assert manager.received_resume_texts == [REALISTIC_RESUME_TEXT]


def test_process_payload_echoes_user_id_when_pending_extraction(worker_factory):
    worker = worker_factory(FakeResumeAnalysisManager(), FakeResumeFileFetcher(text="unused"))

    response = worker.process_payload(
        {"resume_cv": "uploads/resumes/cvs/teste.docx", "user_id": 42}
    )

    assert response.status == "received_pending_extraction"
    assert response.user_id == 42


def test_process_payload_completes_with_only_user_id_and_file_url(worker_factory):
    """The real integration only ever sends `user_id` + a file URL."""
    manager = FakeResumeAnalysisManager()
    fetcher = FakeResumeFileFetcher(text=REALISTIC_RESUME_TEXT)
    worker = worker_factory(manager, fetcher)

    response = worker.process_payload(
        {"resume_cv_url": "http://backend:8000/storage/cv.docx", "user_id": 7}
    )

    assert response.status == "completed"
    assert response.user_id == 7
    assert manager.received_resume_texts == [REALISTIC_RESUME_TEXT]


def test_process_payload_fetches_resume_cv_url_when_no_inline_text(worker_factory):
    manager = FakeResumeAnalysisManager()
    fetcher = FakeResumeFileFetcher(text=REALISTIC_RESUME_TEXT)
    worker = worker_factory(manager, fetcher)

    response = worker.process_payload({"resume_cv_url": "http://backend:8000/storage/cv.docx"})

    assert response.status == "completed"
    assert fetcher.requested_urls == ["http://backend:8000/storage/cv.docx"]
    assert manager.received_resume_texts == [REALISTIC_RESUME_TEXT]


def test_process_payload_returns_pending_when_reference_has_no_scheme(worker_factory):
    worker = worker_factory(FakeResumeAnalysisManager(), FakeResumeFileFetcher(text="unused"))

    response = worker.process_payload({"resume_cv": "uploads/resumes/cvs/teste.docx"})

    assert response.status == "received_pending_extraction"


def test_process_payload_falls_back_to_pending_when_fetch_fails(worker_factory):
    fetcher = FakeResumeFileFetcher(error=RuntimeError("boom"))
    worker = worker_factory(FakeResumeAnalysisManager(), fetcher)

    response = worker.process_payload({"resume_cv_url": "http://backend:8000/storage/cv.docx"})

    assert response.status == "received_pending_extraction"
    assert fetcher.requested_urls == ["http://backend:8000/storage/cv.docx"]


def test_process_payload_rejects_troll_inline_resume_text(worker_factory):
    manager = FakeResumeAnalysisManager()
    worker = worker_factory(manager, FakeResumeFileFetcher())

    troll_text = "kkkkkkkkk teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste teste"
    response = worker.process_payload({"resume_text": troll_text, "user_id": 1})

    assert response.status == "invalid_resume_content"
    assert response.error == "low_content_diversity"
    assert response.result == {}
    assert manager.received_resume_texts == []


def test_process_payload_rejects_too_short_inline_resume_text(worker_factory):
    worker = worker_factory(FakeResumeAnalysisManager(), FakeResumeFileFetcher())

    response = worker.process_payload({"resume_text": "oi", "user_id": 1})

    assert response.status == "invalid_resume_content"
    assert response.error == "too_short"


def test_process_payload_rejects_empty_pdf_extraction(worker_factory):
    """A PDF/DOCX that downloads fine but has no extractable text (e.g. a scanned image)."""
    manager = FakeResumeAnalysisManager()
    fetcher = FakeResumeFileFetcher(text="")
    worker = worker_factory(manager, fetcher)

    response = worker.process_payload({"resume_cv_url": "http://backend:8000/storage/cv.pdf", "user_id": 3})

    assert response.status == "invalid_resume_content"
    assert response.error == "empty"
    assert response.user_id == 3
    assert manager.received_resume_texts == []


def test_process_payload_rejects_troll_pdf_extraction(worker_factory):
    manager = FakeResumeAnalysisManager()
    fetcher = FakeResumeFileFetcher(text=" ".join(["asdkjasd"] * 40))
    worker = worker_factory(manager, fetcher)

    response = worker.process_payload({"resume_cv_url": "http://backend:8000/storage/cv.pdf", "user_id": 3})

    assert response.status == "invalid_resume_content"
    assert response.error == "low_content_diversity"
