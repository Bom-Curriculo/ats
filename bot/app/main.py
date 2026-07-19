from quart import Quart

from app.controllers.analysis_controller import analysis_blueprint
from app.controllers.build_controller import build_blueprint
from app.controllers.health_controller import health_blueprint
from app.core.container import Container
from app.core.logging import configure_logging


def create_app() -> Quart:
    container = Container()
    configure_logging(container.settings().server.log_level)

    container.wire(modules=[
        "app.controllers.analysis_controller",
        "app.controllers.build_controller",
    ])

    quart_app = Quart(__name__)
    quart_app.container = container
    quart_app.register_blueprint(health_blueprint)
    quart_app.register_blueprint(analysis_blueprint)
    quart_app.register_blueprint(build_blueprint)
    return quart_app


app = create_app()
