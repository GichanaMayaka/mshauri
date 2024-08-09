import click
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from config import configs
from mshauri.extensions import db


def database_engine(uri: str) -> Engine:
    return create_engine(uri)


def create_db(uri: PostgresDsn = configs.POSTGRES_DSN) -> None:
    """Creates the Database"""
    engine = database_engine(uri.unicode_string())

    if not database_exists(engine.url):
        create_database(engine.url)


def drop_tables() -> None:
    """Drops tables."""
    if click.confirm("Are you sure?", default=False, abort=True):
        db.drop_all()


def drop_db() -> None:
    """Drops the Database"""
    if click.confirm("Are you sure?", default=False, abort=True):
        engine = database_engine(uri=configs.POSTGRES_DSN.unicode_string())
        if database_exists(engine.url):
            drop_database(engine.url)
