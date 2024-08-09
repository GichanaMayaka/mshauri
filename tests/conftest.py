import pandas as pd
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from ..config import configs
from ..mshauri import create_app, db

engine = create_engine(configs.POSTGRES_DSN.unicode_string())


@pytest.fixture()
def create_test_database(db_engine=engine) -> None:
    if not database_exists(db_engine.url):
        create_database(db_engine.url)


@pytest.fixture()
def app(create_test_database):
    yield create_app()


@pytest.fixture()
def client_app(app: Flask):
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        drop_database(engine.url)


@pytest.fixture()
def test_dataframe():
    test_data = pd.read_excel(
        "./tests/test_data.xlsx",
        header=0,
        nrows=1,
    )

    yield test_data
