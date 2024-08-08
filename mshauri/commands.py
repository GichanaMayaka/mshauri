from flask_sqlalchemy import SQLAlchemy
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_database, database_exists

from ..config import configs
from .extensions import db


def database_engine(uri: str) -> Engine:
    engine = create_engine(uri)
    return engine


def create_db(uri: PostgresDsn = configs.POSTGRES_DSN) -> None:
    engine = database_engine(uri.unicode_string())

    if not database_exists(engine.url):
        create_database(engine.url)


def create_tables(database: SQLAlchemy = db) -> None:
    """Create all tables defined in the model[s]"""
    database.create_all()
