"""Worker RabbitMQ do bot ATS. Execute com ``python -m app.workers.rabbitmq_consumer``."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

import pika

from app.logging_config import configurar_logging
from app.schemas.analise import SolicitacaoAnalise
from app.services.gerenciador_ia import executar_analise_com_fallback
from app.services.rabbitmq_payload_parser import InvalidRabbitMQPayload, parse_rabbitmq_payload

logger = logging.getLogger(__name__)


def _output(data: dict[str, Any], status: str, result: dict[str, Any] | None = None, error: str | None = None) -> dict[str, Any]:
    return {
        "analysis_request_id": data.get("analysis_request_id"),
        "status": status,
        "source": "bot-python",
        "result": result or {},
        "error": error,
    }


def process_payload(data: dict[str, Any]) -> dict[str, Any]:
    curriculo = data.get("curriculo_texto")
    vaga = data.get("vaga_texto")
    if isinstance(curriculo, str) and curriculo.strip() and isinstance(vaga, str) and vaga.strip():
        request = SolicitacaoAnalise(curriculo_texto=curriculo, vaga_texto=vaga)
        result = asyncio.run(executar_analise_com_fallback(request))
        return _output(data, "completed", result.model_dump(mode="json"))

    has_file_reference = any(
        data.get(key)
        for key in ("resume_cv", "resume_cv_url", "resume_linkedin", "resume_linkedin_url", "urls")
    )
    if has_file_reference:
        return _output(data, "received_pending_extraction")
    raise InvalidRabbitMQPayload("mensagem não contém textos analisáveis nem referência de arquivo")


class RabbitMQWorker:
    def __init__(self) -> None:
        credentials = pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "bomcurriculo"),
            os.getenv("RABBITMQ_PASSWORD", "bomcurriculo"),
        )
        self.parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            virtual_host=os.getenv("RABBITMQ_VHOST", "/"),
            credentials=credentials,
            heartbeat=60,
            blocked_connection_timeout=30,
        )
        self.input_queue = os.getenv("RABBITMQ_INPUT_QUEUE", "resumes_queue")
        self.default_output_queue = os.getenv("RABBITMQ_OUTPUT_QUEUE", "resumes_results_queue")

    def _publish(self, channel: Any, queue: str, response: dict[str, Any]) -> None:
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(response, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )

    def _on_message(self, channel: Any, method: Any, _properties: Any, body: bytes) -> None:
        parsed = None
        try:
            parsed = parse_rabbitmq_payload(body)
            response = process_payload(parsed.data)
            output_queue = parsed.data.get("callback_queue") or self.default_output_queue
            self._publish(channel, str(output_queue), response)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("rabbitmq_message_processed", extra={"payload_format": parsed.format, "status": response["status"]})
        except InvalidRabbitMQPayload as exc:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            logger.warning("rabbitmq_message_rejected", extra={"reason": str(exc)})
        except Exception as exc:  # mantém o loop vivo e não expõe dados da mensagem
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
            # Não incluir traceback/mensagem: exceções de validação podem conter
            # trechos do currículo ou outros valores originais.
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
    configurar_logging(os.getenv("LOG_LEVEL", "INFO"))
    while True:
        try:
            RabbitMQWorker().consume()
        except KeyboardInterrupt:
            logger.info("rabbitmq_worker_stopped")
            return
        except Exception as exc:
            logger.error("rabbitmq_connection_failed", extra={"error_type": type(exc).__name__})
            time.sleep(5)


if __name__ == "__main__":
    main()
