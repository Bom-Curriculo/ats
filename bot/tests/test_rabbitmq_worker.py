import pytest

from app.workers.rabbitmq_worker import RabbitMQWorker


class FakeAnalysisResult:
    def model_dump(self, mode: str = "json") -> dict:
        return {"ats_score": 42}


class FakeAIManager:
    def __init__(self) -> None:
        self.received_requests = []

    async def run_analysis_with_fallback(self, request):
        self.received_requests.append(request)
        return FakeAnalysisResult()


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
    def _factory(ai_manager, resume_file_fetcher):
        worker = RabbitMQWorker.__new__(RabbitMQWorker)
        worker._ai_manager = ai_manager
        worker._resume_file_fetcher = resume_file_fetcher
        return worker

    return _factory


def test_process_payload_with_inline_text_completes(worker_factory):
    ai_manager = FakeAIManager()
    worker = worker_factory(ai_manager, FakeResumeFileFetcher())

    response = worker.process_payload(
        {"resume_text": "Python developer", "job_text": "Python required", "analysis_request_id": "abc"}
    )

    assert response.status == "completed"
    assert response.result == {"ats_score": 42}
    assert len(ai_manager.received_requests) == 1


def test_process_payload_fetches_resume_cv_url_when_no_inline_text(worker_factory):
    ai_manager = FakeAIManager()
    fetcher = FakeResumeFileFetcher(text="Extracted resume text")
    worker = worker_factory(ai_manager, fetcher)

    response = worker.process_payload(
        {
            "resume_cv_url": "http://backend:8000/storage/cv.docx",
            "job_text": "Python required",
        }
    )

    assert response.status == "completed"
    assert fetcher.requested_urls == ["http://backend:8000/storage/cv.docx"]
    assert ai_manager.received_requests[0].resume_text == "Extracted resume text"


def test_process_payload_returns_pending_when_reference_has_no_scheme(worker_factory):
    worker = worker_factory(FakeAIManager(), FakeResumeFileFetcher(text="unused"))

    response = worker.process_payload(
        {"resume_cv": "uploads/resumes/cvs/teste.docx", "job_text": "Python required"}
    )

    assert response.status == "received_pending_extraction"


def test_process_payload_falls_back_to_pending_when_fetch_fails(worker_factory):
    fetcher = FakeResumeFileFetcher(error=RuntimeError("boom"))
    worker = worker_factory(FakeAIManager(), fetcher)

    response = worker.process_payload(
        {"resume_cv_url": "http://backend:8000/storage/cv.docx", "job_text": "Python required"}
    )

    assert response.status == "received_pending_extraction"
    assert fetcher.requested_urls == ["http://backend:8000/storage/cv.docx"]
