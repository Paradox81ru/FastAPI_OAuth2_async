import jwt
from fastapi import Depends
from fastapi.security import SecurityScopes
from jwt.exceptions import ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from Auth.db.db_connection import engine, engine_async
from Auth.db.models.jwt_token_manager import JWTTokenManager
from Auth.db.models.user_manager import UserManager
from Auth.exceptions import AuthenticateException
from Auth.schemas import AnonymUser, UerStatus, User, JWTTokenType, UserRoles, BaseUser
from config import get_settings, oauth2_scheme

settings = get_settings()

def get_db_session():
    """
    Синхронная сессия базы данных.
    Есть проблемы при восстановлении миграции в Alembic в асинхронном режиме.
    Поэтому была оставлена синхронная сессия для работы с базой данных.
     """
    with Session(engine) as session:
        yield session

async def get_db_session_async():
    """ Асинхронная сессия базы данных """
    async with AsyncSession(engine_async) as session:
        yield session


async def _validate_token(session: AsyncSession, token: str, jwt_token_type: JWTTokenType) -> dict | None:
    """
    Проверят валидность токена, и если он валидный, то возвращает его содержимое.
    :param session: Сессия для работы с базой данных.
    :param token: Токен.
    :param jwt_token_type: Тип токена (доступа или обновления).
    :return: Раскодированное содержимое токена.
    :raises AuthenticateException:
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
        if not await jwt_token_manager.has_jwt_token(jti):
            # Если нет, то токен не валидный.
            raise AuthenticateException("Could not validate credentials")
        # Если в токене не указан пользователь, то токен не валидный.
        if payload.get('sub') is None:
            raise AuthenticateException("Could not validate credentials")
        return payload
    except ExpiredSignatureError:
        # Если токен просрочен, то он всё равно раскодируется, чтобы найти JTI токена,    
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=['HS256'],
                             options={"verify_signature": False})
        # по которому он удаляется из базы данных.
        await jwt_token_manager.remove_jwt_token(payload.get('jti'))
        raise AuthenticateException("The JWT token is expired")
    except (jwt.InvalidTokenError, ValidationError):
        raise AuthenticateException("The JWT token is damaged")


async def validate_access_token(session: Annotated[AsyncSession, Depends(get_db_session_async)],
                                token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Проверяет валидность токена доступа.
    :param session: Сессия для работы с базой данных.
    :param token: Токен доступа.
    :return: Раскодированное содержимое токена.
    :raises AuthenticateException:
    """
    return await _validate_token(session, token, JWTTokenType.ACCESS)


async def validate_refresh_token(session: Annotated[AsyncSession, Depends(get_db_session_async)],
                                 token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """
    Проверяет валидность токена обновления
    :param session: Сессия для работы с базой данных.
    :param token: Токен обновления.
    :return: Раскодированное содержимое токена.
    :raises AuthenticateException:
    """
    return await _validate_token(session, token, JWTTokenType.REFRESH)


async def get_current_user_and_scope(session: Annotated[AsyncSession, Depends(get_db_session_async)],
                                     payload: Annotated[dict, Depends(validate_access_token)]) -> (BaseUser, list):
    """
    Возвращает пользователя по токену доступа, или анонимного пользователя,
    если токена доступа не было предоставлено вообще. И его scope при авторизации.
    :param session: Сессия для работы с базой данных.
    :param payload: Раскодированное содержимое токена.
    :return: Пользователя и его scope (сфера деятельности).
    :raises AuthenticateException: Не удалось подтвердить учётные данные; Пользователь не доступен.
    """
    user_manager = UserManager(session)
    if payload is None:
        return AnonymUser(), None
    username: str = payload.get('sub')
    scopes = payload.get('scopes')
    user: User = (await user_manager.get_user_schema_by_username(username)).to_user()
    if not user:
        raise AuthenticateException("Could not validate credentials")
    if user.status != UerStatus.ACTIVE:
        raise AuthenticateException("Inactive user")
    return user, scopes


async def check_scope(payload: Annotated[dict, Depends(validate_access_token)], security_scopes: SecurityScopes):
    """
    Проверяет scopes.
    :param payload: Раскодированное содержимое токена.
    :param security_scopes: Список scope для проверки.
    :raises AuthenticateException: Не достаточно прав.
    """
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
    """
    Проверяет роль пользователя.
    :param allowed_roles: Список ролей для проверки.
    :raises AuthenticateException: Не достаточно прав.
    """
    async def _check_role(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
        user, scope = user_and_scope
        if user.role in allowed_roles:
            return
        raise AuthenticateException("Not enough permissions", "Bearer")
    return _check_role


async def is_auth(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """
    Проверят на авторизованного пользователя.
    :param user_and_scope: Текущий пользователь и его scope
     :raises AuthenticateException: Не авторизован.
    """
    user, scope = user_and_scope
    if isinstance(user, AnonymUser):
        raise AuthenticateException("Not authorized", "Bearer")


async def is_not_auth(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """
    Проверят на неавторизованного (анонимного) пользователя.
    :param user_and_scope: Текущий пользователь и его scope.
    """
    user, scope = user_and_scope
    if isinstance(user, User):
        raise AuthenticateException(f"Already authorized username '{user.username}' role {user.get_role()}",
                                    "Bearer")
