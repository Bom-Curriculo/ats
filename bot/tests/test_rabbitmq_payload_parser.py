import json

import pytest

from app.services.parsing.rabbitmq_payload_parser import InvalidRabbitMQPayload, parse_rabbitmq_payload


def test_rabbitmq_payload_parser_behavior_01() -> None:
    payload = {
        "analysis_request_id": "request-123",
        "user_id": 12,
        "resume_cv_url": "http://backend:8000/storage/cv.docx",
        "resume_linkedin_url": "http://backend:8000/storage/linkedin.docx",
        "vaga_texto": "Desenvolvedor Python",
        "callback_queue": "resumes_results_queue",
    }

    parsed = parse_rabbitmq_payload(json.dumps(payload).encode())

    assert parsed.format == "json"
    assert parsed.data == payload


def test_parses_clean_english_json() -> None:
    payload = {
        "analysis_request_id": "request-english",
        "resume_text": "Python project",
        "job_text": "Python required",
        "language": "en-US",
        "job_level": "junior",
        "resume_sources": [],
        "use_ai": False,
    }
    parsed = parse_rabbitmq_payload(json.dumps(payload))
    assert parsed.format == "json"
    assert parsed.data == payload


def test_rabbitmq_payload_parser_behavior_03() -> None:
    command = (
        'O:27:"App\\Jobs\\ProcessResumesJobs":4:{'
        's:9:"resume_cv";s:31:"uploads/resumes/cvs/teste.docx";'
        's:15:"resume_linkedin";s:37:"http://backend:8000/linkedin/teste.pdf";'
        's:7:"user_id";i:12;s:12:"expires_link";s:10:"2026-07-02";}'
    )
    body = json.dumps({"uuid": "job-uuid", "data": {"command": command}})

    parsed = parse_rabbitmq_payload(body)

    assert parsed.format == "laravel"
    assert parsed.data["analysis_request_id"] == "job-uuid"
    assert parsed.data["resume_cv"] == "uploads/resumes/cvs/teste.docx"
    assert parsed.data["resume_linkedin"] == "http://backend:8000/linkedin/teste.pdf"
    assert parsed.data["user_id"] == 12
    assert parsed.data["expires_link"] == "2026-07-02"
    assert parsed.data["urls"] == ["http://backend:8000/linkedin/teste.pdf"]


def test_rabbitmq_payload_parser_behavior_04() -> None:
    command = (
        'O:27:"App\\Jobs\\ProcessResumesJobs":3:{'
        's:12:"\\u0000*\\u0000resume_cv";s:8:"file.pdf";'
        's:10:"\\u0000*\\u0000user_id";i:42;}'
        ' resume_linkedin=http://backend:8000/linkedin.pdf'
    )

    parsed = parse_rabbitmq_payload(json.dumps({"data": {"command": command}}))

    assert parsed.data["resume_cv"] == "file.pdf"
    assert parsed.data["user_id"] == 42
    assert parsed.data["resume_linkedin"] == "http://backend:8000/linkedin.pdf"


@pytest.mark.parametrize("body", [b"not-json", b"[]", b'{"foo":"bar"}', b'{"data":{"command":"other"}}'])
def test_rejects_invalid_payload(body: bytes) -> None:
    with pytest.raises(InvalidRabbitMQPayload):
        parse_rabbitmq_payload(body)
