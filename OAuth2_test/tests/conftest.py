import os
from dataclasses import dataclass
from enum import StrEnum

import httpx
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from config import get_settings

os.environ['IS_TEST'] = 'True'

from main import app
from fastapi.testclient import TestClient

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


class Oauth2Settings(BaseSettings):
    """ Настройки сервера авторизации oauth2. """
    auth_host: str = "localhost"
    auth_port: int = 8001

    secret_key: SecretStr = "15d29aad37ecf71a6094bf2552232839a9df526f968d3c49e6885883892dca01"
    access_token_expire_minutes: int = 5
    refresh_token_expire_minutes: int = 30
    db_connect_str: str = 'sqlite:///db.sqlite3'


    init_admin_email: str = 'admin@mail.com'
    init_system_email: str = 'system@mail.com'
    init_director_login: str = 'Director'
    init_director_name: str = 'Boss'
    init_director_lastname: str = 'Super'
    init_director_email: str = 'boss@mail.com'
    init_user_login: str = 'User'
    init_user_name: str = ''
    init_user_lastname: str = ''
    init_user_email: str = 'user@mail.com'

    init_admin_password: SecretStr = "Password_123"
    init_system_password: SecretStr = "Password_123"
    init_director_password: SecretStr = "Password_123"
    init_user_password: SecretStr = "Password_123"


@pytest.fixture()
def client():
    """ Тестовый клиент. """
    return TestClient(app)


@pytest.fixture(scope='session')
def api_settings():
    """ Класс настроек oauth2_test """
    return get_settings()


@pytest.fixture(scope='session')
def oauth2_settings():
    """ Класс настроек oauth2. """
    env_path = os.path.join(os.getcwd(), '..', 'oauth2', 'Auth', '.env')
    load_dotenv(env_path)
    return Oauth2Settings()


@pytest.fixture(scope='session')
def users_data(oauth2_settings) -> dict[UserType, UserAuth]:
    """
    Данные для авторизации пользователя (логин и пароль).
    :param oauth2_settings: Настройки сервера авторизации oauth2.
    :return:
    """
    users_data = {UserType.ADMIN: UserAuth(
                      UserType.ADMIN, oauth2_settings.init_admin_password.get_secret_value()),
                  UserType.SYSTEM: UserAuth(
                      UserType.SYSTEM, oauth2_settings.init_system_password.get_secret_value()),
                  UserType.DIRECTOR: UserAuth(
                      oauth2_settings.init_director_login,
                      oauth2_settings.init_director_password.get_secret_value()),
                  UserType.USER: UserAuth(
                      oauth2_settings.init_user_login,
                      oauth2_settings.init_user_password.get_secret_value())}
    return users_data


@pytest.fixture(scope='session')
def oauth_server(api_settings):
    """ URL сервера авторизации. """
    return  f"http://{api_settings.auth_server_host}:{api_settings.auth_server_port}"


def get_access_token(user_auth: UserAuth, oauth_server, scope: list[str]):
    """
    Возвращает токен авторизации.
    :param user_auth: Логин и пароль пользователя.
    :param oauth_server: URL сервера авторизации.
    :param scope: Список scope авторизации.
    :return: Токен доступа.
    """
    api_url = f"{oauth_server}/api/oauth/token"
    request_data = {'username': user_auth.username, 'password': user_auth.password, 'scope': " ".join(scope)}
    with httpx.Client() as client:
        response = client.post(api_url, data=request_data)
        return response.json()['access_token']