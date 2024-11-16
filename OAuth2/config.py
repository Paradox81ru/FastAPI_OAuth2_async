import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import SecretStr
from pydantic_settings import BaseSettings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(
    auto_error=False,
    tokenUrl='/api/oauth/token',
    scopes={"me": "Read information about the current user.", "items": "Read items."}
)

class Settings(BaseSettings):
    secret_key: SecretStr = "15d29aad37ecf71a6094bf2552232839a9df526f968d3c49e6885883892dca01"
    access_token_expire_minutes: int = 5
    refresh_token_expire_minutes: int = 30
    db_connect_str: str = 'sqlite+aiosqlite:///db.sqlite3'

    init_admin_password: SecretStr = "Cucumber_123"
    init_system_password: SecretStr = "Cucumber_123"
    init_director_password: SecretStr = "Cucumber_123"
    init_user_password: SecretStr = "Cucumber_123"


# @lru_cache
def get_settings():
    env_path = os.path.join(os.getcwd(), 'tests', '.env') if ('IS_TEST' in os.environ and os.environ['IS_TEST'] == 'True') \
                else os.path.join(os.getcwd(),'OAuth2', '.env')
    load_dotenv(env_path) 
    return Settings()