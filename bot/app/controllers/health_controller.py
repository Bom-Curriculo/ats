import logging

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from quart import Blueprint

from app.models.health_status import HealthStatus

logger = logging.getLogger(__name__)

health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/health")
async def health_check() -> dict[str, str]:
    logger.info("health check ok")
    return HealthStatus().model_dump()


@health_blueprint.get("/metrics")
async def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
