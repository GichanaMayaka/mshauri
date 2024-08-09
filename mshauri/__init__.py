import atexit
from http import HTTPStatus

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from pydantic import PostgresDsn

from ..config import configs
from .commands import create_db, drop_db, drop_tables, data, DATASET
from .extensions import db, migrate
from .models import CME, Drill, MentorsChecklist
from .transformer.transformer import parser


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

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=task, args=[DATASET], trigger="interval", seconds=300)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=True))

    register_extensions(app)
    register_commands(app)

    @app.route("/", methods=["GET"])
    def index() -> tuple[str, int]:
        return (
            "Welcome to Mshauri",
            HTTPStatus.OK,
        )

    @app.route("/run", methods=["GET"])
    def process():
        task(DATASET)

        return {
            "message": "Processed Successfully",
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
    """Register commands

    Args:
        app (Flask): Flask Instance
    """
    for command in [create_db, drop_tables, drop_db, data]:
        app.cli.command()(command)


def task(source: pd.DataFrame) -> pd.DataFrame:
    """Task that performs the transformation

    Returns:
        pd.DataFrame: The resultant dataframe
    """
    app = create_app()
    with app.app_context():
        # If executed outside of app context
        output = parser(source)

        return output
