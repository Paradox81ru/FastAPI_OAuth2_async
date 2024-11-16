import os
os.environ['IS_TEST'] = 'True'

from fastapi.testclient import TestClient
from main import app
from OAuth2.config import get_settings
from OAuth2.db.db_connection import db_session as session
import alembic.config
import alembic.environment

import alembic
import pytest


@pytest.fixture(autouse=True, scope='session')
def setup():
    # Перед началом теста тестовая база удаляется,
    if os.path.exists('db-test.sqlite3'):
        os.remove('db-test.sqlite3')

    alembic_cfg = alembic.config.Config('alembic.ini')
    # и с помощью alembic инициируется новая тестовая база.
    alembic.command.upgrade(alembic_cfg, 'head')
    yield
   
   
@pytest.fixture()
def db_session():
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def api_settings():
    return get_settings()