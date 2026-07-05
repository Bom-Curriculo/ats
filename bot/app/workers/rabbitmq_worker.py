"""ATS bot RabbitMQ worker. Run with ``python -m app.workers.rabbitmq_worker``."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import pika

from app.core.logging import configure_logging
from app.core.settings import Settings
from app.models.analysis import AnalysisRequest
from app.models.rabbitmq_output import RabbitMQOutputMessage
from app.services.ai.interfaces import AIManagerInterface
from app.services.ai.ai_manager import AIManager
from app.services.parsing.interfaces import RabbitMQPayloadParserInterface, ResumeFileFetcherInterface
from app.services.parsing.rabbitmq_payload_parser import InvalidRabbitMQPayload, RabbitMQPayloadParser
from app.services.parsing.resume_file_fetcher import ResumeFileFetcher

_FILE_REFERENCE_FIELDS = ("resume_cv_url", "resume_cv", "resume_linkedin_url", "resume_linkedin")

logger = logging.getLogger(__name__)


def _output(data: dict[str, Any], status: str, result: dict[str, Any] | None = None, error: str | None = None) -> RabbitMQOutputMessage:
    return RabbitMQOutputMessage(
        analysis_request_id=data.get("analysis_request_id"),
        status=status,
        result=result or {},
        error=error,
    )


class RabbitMQWorker:
    def __init__(
        self,
        settings: Settings | None = None,
        ai_manager: AIManagerInterface | None = None,
        payload_parser: RabbitMQPayloadParserInterface | None = None,
        resume_file_fetcher: ResumeFileFetcherInterface | None = None,
    ) -> None:
        self._settings = settings or Settings.load()
        self._ai_manager = ai_manager or AIManager(self._settings)
        self._payload_parser = payload_parser or RabbitMQPayloadParser()
        self._resume_file_fetcher = resume_file_fetcher or ResumeFileFetcher()

        rabbitmq = self._settings.rabbitmq
        credentials = pika.PlainCredentials(rabbitmq.user, rabbitmq.password)
        self.parameters = pika.ConnectionParameters(
            host=rabbitmq.host,
            port=rabbitmq.port,
            virtual_host=rabbitmq.vhost,
            credentials=credentials,
            heartbeat=rabbitmq.heartbeat_seconds,
            blocked_connection_timeout=rabbitmq.blocked_connection_timeout_seconds,
        )
        self.input_queue = rabbitmq.input_queue
        self.default_output_queue = rabbitmq.output_queue

    def process_payload(self, data: dict[str, Any]) -> RabbitMQOutputMessage:
        return asyncio.run(self._process_payload_async(data))

    async def _process_payload_async(self, data: dict[str, Any]) -> RabbitMQOutputMessage:
        resume = data.get("resume_text", data.get("curriculo_texto"))
        if not (isinstance(resume, str) and resume.strip()):
            resume = await self._extract_resume_text_from_file_reference(data)
        job = data.get("job_text", data.get("vaga_texto"))

        if isinstance(resume, str) and resume.strip() and isinstance(job, str) and job.strip():
            request = AnalysisRequest.model_validate({**data, "resume_text": resume, "job_text": job})
            result = await self._ai_manager.run_analysis_with_fallback(request)
            return _output(data, "completed", result.model_dump(mode="json"))

        has_file_reference = any(data.get(key) for key in (*_FILE_REFERENCE_FIELDS, "urls"))
        if has_file_reference:
            return _output(data, "received_pending_extraction")
        raise InvalidRabbitMQPayload("message contains neither analyzable text nor a file reference")

    async def _extract_resume_text_from_file_reference(self, data: dict[str, Any]) -> str | None:
        """Fetch and extract text from the first downloadable file reference.

        Only fields already holding an absolute http(s) URL are attempted —
        a bare storage path (e.g. ``uploads/resumes/cvs/foo.docx``) has no
        known host to fetch from and is left for ``received_pending_extraction``.
        """
        for field in _FILE_REFERENCE_FIELDS:
            value = data.get(field)
            if not (isinstance(value, str) and value.lower().startswith(("http://", "https://"))):
                continue
            try:
                return await self._resume_file_fetcher.fetch_and_extract_text(value)
            except Exception as exc:
                logger.warning(
                    "rabbitmq_file_reference_fetch_failed",
                    extra={"field": field, "error_type": type(exc).__name__},
                )
        return None

    def _publish(self, channel: Any, queue: str, response: RabbitMQOutputMessage) -> None:
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=response.to_json_bytes(),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )

    def _on_message(self, channel: Any, method: Any, _properties: Any, body: bytes) -> None:
        parsed = None
        try:
            parsed = self._payload_parser.parse(body)
            response = self.process_payload(parsed.data)
            output_queue = parsed.data.get("callback_queue") or self.default_output_queue
            self._publish(channel, str(output_queue), response)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("rabbitmq_message_processed", extra={"payload_format": parsed.format, "status": response.status})
        except InvalidRabbitMQPayload as exc:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            logger.warning("rabbitmq_message_rejected", extra={"reason": str(exc)})
        except Exception as exc:  # Keep the loop alive without exposing message data.
            if parsed is not None:
                try:
                    queue = parsed.data.get("callback_queue") or self.default_output_queue
                    self._publish(channel, str(queue), _output(parsed.data, "failed", error=type(exc).__name__))
                except Exception as publish_exc:
                    logger.error(
                        "rabbitmq_failure_response_publish_failed",
                        extra={"error_type": type(publish_exc).__name__},
                    )
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            # Never log the raw exception message: it may embed resume excerpts
            # or other original values from the payload being processed.
            logger.error("rabbitmq_message_processing_failed", extra={"error_type": type(exc).__name__})

    def consume(self) -> None:
        connection = pika.BlockingConnection(self.parameters)
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.input_queue, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=self.input_queue, on_message_callback=self._on_message)
            logger.info("rabbitmq_worker_started", extra={"input_queue": self.input_queue})
            channel.start_consuming()
        finally:
            if connection.is_open:
                connection.close()


def main() -> None:
    settings = Settings.load()
    configure_logging(settings.server.log_level)
    while True:
        try:
            RabbitMQWorker(settings).consume()
        except KeyboardInterrupt:
            logger.info("rabbitmq_worker_stopped")
            return
        except Exception as exc:
            logger.error("rabbitmq_connection_failed", extra={"error_type": type(exc).__name__})
            time.sleep(5)


if __name__ == "__main__":
    main()
