import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
# from passlib.context import CryptContext
from pwdlib import PasswordHash
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from Auth.base import AbstractPwdContext

oauth2_scheme = OAuth2PasswordBearer(
    auto_error=False,
    tokenUrl='/api/oauth/token',
    scopes={"me": "Read information about the current user.", "items": "Read items."}
)

# Корневой каталог проекта
root_path = Path(__file__).resolve().parents[0]

LOGGER_FILENAME = Path(root_path, 'logs', 'OAuth2.log')
templates = Jinja2Templates(directory="ui/jinja2")


def get_logger(logger_name: str) -> logging.Logger:
    """
    Возвращает логгер
    :param logger_name: Наименование логгера.
    :return:
    """
    logger = logging.getLogger(logger_name)

    create_logs_dir()
    logger_handler = logging.FileHandler(LOGGER_FILENAME, mode='a')
    logger_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)
    # self.set_logger_level(logging.ERROR)
    is_debug_mode = os.getenv('DEBUG_MODE') in ('True', 'true')
    logger.setLevel(logging.DEBUG if is_debug_mode else logging.ERROR)
    return logger


def create_logs_dir():
    """ Проверяет наличие каталогов с логами, и если нет, создаёт его. """
    parent_dir = Path(LOGGER_FILENAME).parent
    if not parent_dir.exists():
        parent_dir.mkdir()


class MyPwdContext(AbstractPwdContext):
    """ Конкретный класс для управления криптографией пароля. """
    def __init__(self, pwd_context):
        self._pwd_context = pwd_context

    def hash(self, password) -> str:
        return self._pwd_context.hash(password)

    def verify(self, password, _hash) -> bool:
        return self._pwd_context.verify(password, _hash)


class Settings(BaseSettings):
    """ Класс настроек приложения """
    auth_host: str = "localhost"
    auth_port: int = 8001

    secret_key: SecretStr = "15d29aad37ecf71a6094bf2552232839a9df526f968d3c49e6885883892dca01"
    access_token_expire_minutes: int = 5
    refresh_token_expire_minutes: int = 30
    db_connect_str: str = 'sqlite+aiosqlite:///db.sqlite3'

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

    debug_mode: bool = False


def get_pwd_context():
    """ Возвращает класс работы с паролем. """
    # pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    # Почему то библиотека passlib не хочет работать, возможно проблема, давнее отсутствие поддержки данной библиотеки.
    pwd_context = PasswordHash.recommended()
    # По этой причине пока что используется более современная библиотека pwdlib.
    my_pwd_context = MyPwdContext(pwd_context)
    return my_pwd_context


# @lru_cache
def get_settings():
    """ Возвращает класс настроек приложения. """
    env_path = os.path.join(os.getcwd(), 'tests', '.env') \
        if ('IS_TEST' in os.environ and os.environ['IS_TEST'] == 'True') \
        else os.path.join(os.getcwd(), 'Auth', '.env')
    load_dotenv(env_path) 
    return Settings()
