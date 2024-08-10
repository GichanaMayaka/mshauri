import atexit
from http import HTTPStatus

import pandas as pd
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flasgger import Swagger
from flask import Flask, request
from pydantic import PostgresDsn

from config import configs
from mshauri.commands import create_db, drop_db, drop_tables
from mshauri.extensions import db, migrate
from mshauri.models import MentorsChecklist, CME, Drill
from mshauri.transformer.transformer import parser

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
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.unicode_string()
    app.config["SECRET_KEY"] = configs.SECRET_KEY

    swag = Swagger(app, template_file="./api-docs.yml")

    register_extensions(app)
    register_commands(app)

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=task,
        args=[SOURCE, app],
        trigger="interval",
        seconds=300,
        id="parse_dataset",
    )
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown(wait=True))

    @app.route("/", methods=["GET"])
    def index() -> tuple[str, int]:
        return (
            "Welcome to Mshauri",
            HTTPStatus.OK,
        )

    @app.route("/checklists", methods=["GET"])
    def get_checklists() -> tuple[dict, int]:
        checklists = MentorsChecklist.query.limit(500).all()

        if checklists:
            return {"checklists": checklists}, HTTPStatus.OK

        return {"message": "Not Found"}, HTTPStatus.NOT_FOUND

    @app.route("/schedule", methods=["POST"])
    def modify_trigger() -> tuple[dict, int]:
        data = request.get_json()
        trigger = data.get("schedule")

        if not trigger:
            return {
                "message": "Please specify a Cron expression under the 'schedule' key"
            }, HTTPStatus.BAD_REQUEST

        try:
            cron_trigger = CronTrigger.from_crontab(trigger)
            job = scheduler.get_job("parse_dataset")

            if job:
                job.modify(trigger=cron_trigger)
                message = "Job trigger modified successfully!"

            else:
                # If the job doesn't exist, add a new job
                message = "No jobs currently scheduled"
                return {
                    "error": "No Job[s] found",
                    "detail": message,
                }, HTTPStatus.NOT_FOUND

        except ValueError as e:
            return {
                "error": "Invalid cron expression",
                "details": str(e),
            }, HTTPStatus.BAD_REQUEST

        except ConflictingIdError as e:
            return {
                "error": "Job ID conflict",
                "details": str(e),
            }, HTTPStatus.BAD_REQUEST

        return {"message": message}, HTTPStatus.OK

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
    """Task that performs the transformation"""
    with app.app_context():
        df = pd.read_excel(source)
        parser(df)
