import jwt
from fastapi import Depends
from fastapi.security import SecurityScopes
from jwt.exceptions import ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from OAuth2.config import get_settings, oauth2_scheme
from OAuth2.db.db_connection import db_session
from OAuth2.exceptions import AuthenticateException
from OAuth2.schemas import AnonymUser, UerStatus, User, JWTTokenType, UserRoles
from OAuth2.db.models.user_manager import UserManager
from OAuth2.db.models.jwt_token_manager import JWTTokenManager

settings = get_settings()


async def get_db_session():
    try:
        yield db_session
    finally:
        db_session.close()

def _validate_token(session: AsyncSession, token: str, jwt_token_type: JWTTokenType) -> dict | None:
    """
    Проверят валидность токена, и если он валидный, то возвращает его содержимое
    :return : payload
    """
    jwt_token_manager = JWTTokenManager(session)
    if token is None:
        return None
    try:
        payload: dict = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=['HS256'])
        if payload.get('type') != jwt_token_type:
             raise AuthenticateException("The JWT token is damaged")
        jti: str = payload.get('jti')
        # Проверка, есть ли этот токен в базе.
        if not jwt_token_manager.has_jwt_token(jti):
            # Если нет, то токен не валидный.
            raise AuthenticateException("Could not validate credentials")
        # Если в токене не указан пользователь, то токен не валидный.
        if payload.get('sub') is None:
            raise AuthenticateException("Could not validate credentials")
        return payload
    except ExpiredSignatureError as err:
        # Если токен просрочен, то он всё равно раскодируется, чтобы найти JTI токена,    
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=['HS256'], options={"verify_signature": False})
        # по которому он удаляется из базы данных.
        jwt_token_manager.remove_jwt_token(payload.get('jti'))
        raise AuthenticateException("The JWT token is expired")
    except (jwt.InvalidTokenError, ValidationError):
        raise AuthenticateException("The JWT token is damaged")


async def validate_access_token(session: Annotated[AsyncSession, Depends(get_db_session)], token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Проверяет валидность токена доступа
    :return : payload - содержимое токена
    """
    return _validate_token(session, token, JWTTokenType.ACCESS)

async def validate_refresh_token(session: Annotated[AsyncSession, Depends(get_db_session)], token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Проверяет валидность токена обновления
    :return : payload - содержимое токена
    """
    return _validate_token(session, token, JWTTokenType.REFRESH)


async def get_current_user(session: Annotated[AsyncSession, Depends(get_db_session)], payload: Annotated[dict, Depends(validate_access_token)]):
    """ Возвращает пользователя по токену доступа, или анонимного пользователя, если токена доступа не было предоставлено вообще """
    user_manager = UserManager(session)
    if payload is None:
        return AnonymUser()
    username: str = payload.get('sub')
    user: User = user_manager.get_user_schema_by_username(username).to_user()
    if not user:
        raise AuthenticateException("Could not validate credentials")
    if user.status != UerStatus.ACTIVE:
        raise AuthenticateException("Inactive user")
    return user


def check_scope(payload: Annotated[dict, Depends(validate_access_token)], security_scopes: SecurityScopes):
    """ Проверяет scopes """
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    if len(security_scopes.scopes) == 0:
        return
    if payload is None:
        raise AuthenticateException("Not enough permissions", authenticate_value)
    token_scopes = payload.get('scopes', [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise AuthenticateException("Not enough permissions", authenticate_value)


def check_role(allowed_roles: tuple[str, ...] | list[str] | list[UserRoles]):
    """ Проверяет роль пользователя """
    def _check_role(user: Annotated[User, Depends(get_current_user)]):
        if user.role in allowed_roles:
            return True
        raise AuthenticateException("Not enough permissions", "Bearer")
    return _check_role


def is_auth(user: Annotated[User, Depends(get_current_user)]):
    """ Проверят на авторизованного пользователя """
    if isinstance(user, AnonymUser):
        raise AuthenticateException("Not authorized", "Bearer")


def is_not_auth(user: Annotated[User, Depends(get_current_user)]):
    """ Проверят на неавторизованного пользователя """
    if isinstance(user, User):
        raise AuthenticateException(f"Already authorized username '{user.username}' role {user.get_role()}", "Bearer")