import atexit
from http import HTTPStatus

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from pydantic import PostgresDsn

from config import configs
from mshauri.commands import create_db, drop_db, drop_tables
from mshauri.extensions import db, migrate
from mshauri.models import MentorsChecklist
from mshauri.transformer import parser


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

    source = "./mshauri/dataset/data.xlsx"  # Path to the dataset

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=task, args=[source, app], trigger="interval", seconds=300)
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
    def process() -> tuple[dict, int]:
        return {
            "message": "Processed Successfully",
        }, HTTPStatus.OK

    @app.route("/checklist", methods=["GET"])
    def get_checklists() -> tuple[dict, int]:
        checklists = MentorsChecklist.query.all()

        return {"checklists": checklists}, HTTPStatus.OK

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
    for command in [
        create_db,
        drop_tables,
        drop_db,
    ]:
        app.cli.command()(command)


def task(source: str, app: Flask) -> None:
    """Task that performs the transformation

    Returns:
        pd.DataFrame: The resultant dataframe
    """
    with app.app_context():
        df = pd.read_excel(source)
        parser(df)
