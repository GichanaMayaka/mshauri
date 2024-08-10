from http import HTTPStatus

from flasgger import Swagger
from flask import Flask, request
from pydantic import PostgresDsn

from config import configs
from mshauri.commands import create_db, drop_db, drop_tables
from mshauri.controllers import bp
from mshauri.extensions import db, migrate
from mshauri.models import CME, Drill, MentorsChecklist

SOURCE = "./mshauri/dataset/data.xlsx"  # Path to the dataset


def create_app(database_url: PostgresDsn = configs.POSTGRES_DSN) -> Flask:
    """App factory

    Args:
        database_url (PostgresDsn, optional): The database URI.
        Defaults to configs.POSTGRES_DSN.

    Returns:
        Flask: The resultant Flask instance
    """
    app = Flask(__name__)
    swag = Swagger(app, template_file="./controllers/api-docs.yml")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.unicode_string()
    app.config["SECRET_KEY"] = configs.SECRET_KEY

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)

    @app.route("/", methods=["GET"])
    def index() -> tuple[str, int]:
        return (
            "Welcome to Mshauri",
            HTTPStatus.OK,
        )

    @app.after_request
    def set_headers(response):
        response.headers["Access-Control-Allow-Origin"] = configs.ALLOWED_ORIGINS
        response.headers["Access-Control-Allow-Methods"] = "GET, POST"

        if "flasgger.apidocs" not in request.endpoint:
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
    """Register commands

    Args:
        app (Flask): Flask Instance
    """
    for command in [
        create_db,
        drop_tables,
        drop_db,
    ]:
        app.cli.command()(command)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(bp)
