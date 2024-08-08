from http import HTTPStatus

from flask import Flask
from pydantic import PostgresDsn

from ..config import configs
from .commands import create_db, create_tables
from .extensions import db, migrate
from .models import CME, Drill, MentorsChecklist


def create_app(database_url: PostgresDsn = configs.POSTGRES_DSN) -> Flask:
    """App factory

    Args:
        database_url (PostgresDsn, optional): The database URI.
        Defaults to configs.POSTGRES_DSN.

    Returns:
        Flask: The resultant Flask instance
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.unicode_string()
    app.config["SECRET_KEY"] = configs.SECRET_KEY

    register_extensions(app)
    register_commands(app)
    # register_blueprints(app)

    @app.route("/", methods=["GET"])
    def index() -> tuple[str, int]:
        return (
            "Welcome to Mshauri",
            HTTPStatus.OK,
        )

    @app.route("/process", methods=["GET"])
    def process():
        return {
            "message": "Started Processing",
        }, HTTPStatus.OK

    @app.after_request
    def set_headers(response):
        response.headers["Access-Control-Allow-Origin"] = configs.ALLOWED_ORIGINS
        response.headers["Access-Control-Allow-Methods"] = "GET, POST"
        response.headers["Content-Type"] = "application/json"
        response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type"
        return response

    return app


def register_extensions(app: Flask) -> None:
    """Register extensions

    Args:
        app (Flask): Flask Instance
    """
    db.init_app(app)
    migrate.init_app(app, db=db)


def register_commands(app: Flask) -> None:
    for command in [create_db, create_tables]:
        app.cli.command()(command)
