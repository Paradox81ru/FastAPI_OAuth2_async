import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

# Корневой каталог проекта
root_path = Path(__file__).resolve().parents[0]
aa = 2

LOGGER_FILENAME = Path(root_path, 'logs','OAuth2_test.log' )
templates = Jinja2Templates(directory="ui/jinja2")


def get_logger(logger_name: str) -> logging.Logger:
    """ Возвращает логгер. """
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


def create_logs_dir():
    """ Проверяет наличие каталогов с логами, и если нет, создаёт ешл """
    parent_dir = Path(LOGGER_FILENAME).parent
    if not parent_dir.exists():
        parent_dir.mkdir()


class Settings(BaseSettings):
    """ Класс настроек. """
    auth_test_host: str = "localhost"
    auth_test_port: int = 8000

    auth_server_host: str = "localhost"
    auth_server_port: int = 8001


# @lru_cache
def get_settings():
    """ Возвращает класс настроек. """
    env_path = os.path.join(os.getcwd(), 'tests', '.env') if ('IS_TEST' in os.environ and os.environ['IS_TEST'] == 'True') \
                else os.path.join(os.getcwd(),'fastapi_site', '.env')
    load_dotenv(env_path) 
    return Settings()