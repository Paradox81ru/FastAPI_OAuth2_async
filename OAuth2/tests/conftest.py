import os
from dataclasses import dataclass
from enum import StrEnum

os.environ['IS_TEST'] = 'True'

from httpx import ASGITransport, AsyncClient
from main import app
from config import get_settings
from Auth.db.db_connection import engine_async
from sqlalchemy.ext.asyncio import AsyncSession
import alembic.config
import alembic.environment

import alembic
import pytest


class UserType(StrEnum):
    """ Типы пользователей. """
    ADMIN = 'Admin'
    SYSTEM = 'System'
    DIRECTOR = 'Director'
    USER = "User"
    ANONYM = "Anonym"


@dataclass
class UserAuth:
    """ Модель авторизации пользователя. """
    username: str
    password: str


async def get_access_token(async_client: AsyncClient, user_auth: UserAuth, scope: list[str]):
    """
    Возвращает токен авторизации.
    :param async_client: Асинхронный тестовый клиент.
    :param user_auth: Логин и пароль пользователя.
    :param scope: Список scope при авторизации.
    :return: Токен доступа.
    """
    request_data = {'username': user_auth.username, 'password': user_auth.password, 'scope': " ".join(scope)}
    response = await async_client.post("/api/oauth/token", data=request_data)
    return response.json()['access_token']


@pytest.fixture(scope='session')
def users_data(api_settings) -> dict[UserType, UserAuth]:
    """
    Данные для авторизации пользователя (логин и пароль).
    :param api_settings: Настройки приложения.
    :return:
    """
    users_data = {UserType.ADMIN: UserAuth(
                      UserType.ADMIN, api_settings.init_admin_password.get_secret_value()),
                  UserType.SYSTEM: UserAuth(
                      UserType.SYSTEM, api_settings.init_system_password.get_secret_value()),
                  UserType.DIRECTOR: UserAuth(
                      api_settings.init_director_login,
                      api_settings.init_director_password.get_secret_value()),
                  UserType.USER: UserAuth(
                      api_settings.init_user_login,
                      api_settings.init_user_password.get_secret_value())}
    return users_data


@pytest.fixture(autouse=True, scope='session')
def setup():
    """ Инициализация перед началом тестов. """
    # Перед началом теста тестовая база удаляется,
    if os.path.exists('db-test.sqlite3'):
        os.remove('db-test.sqlite3')

    # и с помощью alembic инициируется новая тестовая база.
    alembic_cfg = alembic.config.Config('alembic.ini')
    # noinspection PyUnresolvedReferences
    alembic.command.upgrade(alembic_cfg, 'head')
    yield
   
   
@pytest.fixture()
async def db_session():
    """ Сессия для работы с базой данных. """
    async with AsyncSession(engine_async) as session:
        yield session


# @pytest.fixture()
# def client():
#     """ Тестовый клиент. """
#     return TestClient(app)

@pytest.fixture()
async def async_client(api_settings) -> AsyncClient:
    """ Асинхронный тестовый клиент """
    async with AsyncClient(
        transport=ASGITransport(app=app),
            base_url=f"http://test") as ac:
        yield ac


@pytest.fixture(scope='session')
def api_settings():
    """ Настройки приложения. """
    return get_settings()
