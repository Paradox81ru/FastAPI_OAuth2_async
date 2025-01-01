from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from Auth.db.models.jwt_token_manager import JWTTokenManager
from Auth.db.models.user_manager import UserManager
from Auth.dependencies import get_db_session_async, validate_refresh_token, get_current_user_and_scope
from Auth.schemas import Token, User, AnonymUser
from config import get_settings

settings = get_settings()

router = APIRouter(
    prefix='/oauth',
    tags=['oauth'])


@router.post("/token")
async def login_for_access_token(db_session: Annotated[AsyncSession, Depends(get_db_session_async)],
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Выдаёт токен доступа при авторизации.
    :param db_session: Сессия работы с базой данных.
    :param form_data: Данные из формы логин-пароля.
    :return: Кортеж, состоящий из токен доступа, токена обновления и тип авторизации.
    :raises HTTPException: Неверный логин или пароль.
    """
    user_manager = UserManager(db_session)
    jwt_token_manager = JWTTokenManager(db_session)
    user = await user_manager.get_authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = await jwt_token_manager.create_access_token(user.username, data={'scopes': form_data.scopes})
    refresh_token = await jwt_token_manager.create_refresh_token(user.username, data={'scopes': form_data.scopes})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/token-refresh")
async def refresh_access_token(db_session: Annotated[AsyncSession, Depends(get_db_session_async)],
                               payload: Annotated[dict, Depends(validate_refresh_token)]):
    """
    Обновление токена доступа.
    :param db_session: Сессия работы с базой данных.
    :param payload: Данные из полученного токена.
    :return:
    """
    jwt_token_manager = JWTTokenManager(db_session)
    jti = payload.get('jti')
    username = payload.get('sub')
    scopes = payload.get('scopes')

    access_token = await jwt_token_manager.create_access_token(username, data={'scopes': scopes})
    refresh_token = await jwt_token_manager.create_refresh_token(username, data={'scopes': scopes})
    # Из базы удаляется только токен обновления, а токен доступа пока что остаётся в базе. Поэтому
    # далее нужна периодическая задача по удалению всех просроченных токенов из базы данных.
    await jwt_token_manager.remove_jwt_token(jti)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.get("/get_user", response_model=tuple[User, list] | tuple[AnonymUser, None])
async def get_user(current_user: Annotated[tuple[User, list] | tuple[AnonymUser, None],
                   Depends(get_current_user_and_scope)]):
    """
    Возвращает пользователя и его scope, по переданному токену доступа.
    :param current_user: Кортеж, текущий пользователь и его scope.
    :return: Кортеж, пользователь и его scope.
    """
    return current_user

# @router.get("/signup")
# async def signup(db_session: Annotated[Session, Depends(get_db_session)]):
#     """ Регистрация нового пользователя """
#     return {"message": "signup"}
