import logging
import sys

from pythonjsonlogger import jsonlogger


def configurar_logging(nivel: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
    )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(nivel)

    for nome_logger in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(nome_logger).handlers = [handler]
