import click
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from ..config import configs
from .extensions import db
import pandas as pd


# Updated by the data command through CLI
DATASET: pd.DataFrame | None = None


def database_engine(uri: str) -> Engine:
    return create_engine(uri)


def create_db(uri: PostgresDsn = configs.POSTGRES_DSN) -> None:
    engine = database_engine(uri.unicode_string())

    if not database_exists(engine.url):
        create_database(engine.url)


def drop_tables() -> None:
    """Drops tables."""
    if click.confirm("Are you sure?", default=False, abort=True):
        db.drop_all()


def drop_db() -> None:
    if click.confirm("Are you sure?", default=False, abort=True):
        engine = database_engine(uri=configs.POSTGRES_DSN.unicode_string())
        if database_exists(engine.url):
            drop_database(engine.url)


@click.argument("source")
def data(source):
    try:
        DATASET = pd.read_excel(source)
        click.echo(DATASET.head())

    except FileNotFoundError:
        click.echo(
            click.style(
                "The file you're referencing doesn't exist. Please try another file",
                fg="red",
            )
        )
