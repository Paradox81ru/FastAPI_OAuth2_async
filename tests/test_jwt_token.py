from datetime import datetime, timedelta
from typing import final

import pytest
from sqlalchemy import select, func
from OAuth2.db.models.user import User
from OAuth2.db.models.user_manager import UserManager
from OAuth2.db.models.jwt_token import JWTToken
from OAuth2.db.models.jwt_token_manager import JWTTokenManager
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from tests.conftest import db_session


async def _add_jwt_token(db_session: AsyncSession, lifetime: int, username: str):
    """
    Добавляет данные о JWT токене
    :param db_session: сессия для работы с БД
    :param lifetime: время истечения срока токена в минутах
    :param username: имя пользователя, на которого выписывается токен
    :return : уникальный UUID код токена
    """
    jwt_token_manger = JWTTokenManager(db_session)
    jti = uuid.uuid4()
    data_expire = datetime.now() + timedelta(minutes=lifetime)
    await jwt_token_manger.add_jwt_token(jti, data_expire, username)
    assert await jwt_token_manger.has_jwt_token(jti)
    return jti


@pytest.mark.asyncio
async def test_jwt_token(db_session: AsyncSession):
    """ Тестирует создание, поиск и удаление JWT токенов """
    jwt_token_manager = JWTTokenManager(db_session)
    user_manager = UserManager(db_session)
    username: final = 'User'

    jti = uuid.uuid4()
    assert not await jwt_token_manager.has_jwt_token(jti)

    await _add_jwt_token(db_session, -1, username)
    jti = await _add_jwt_token(db_session, -1, username)

    # Общее количество токенов у пользователя.
    token_count = await jwt_token_manager.get_user_jwt_token_count(username)
    assert token_count == 2

    # token: JWTToken = jwt_token_manager.get_jwt_token(jti)
    # user: User = token.subject
    # stmt = select(User).options(selectinload(User.jwt_tokens))
    user = await user_manager.get_user_by_jwt_token(jti)
    assert user.username == username
    # вместо 'options(selectinload(User.jwt_tokens))' в запросе, просто догружаются данные указанного поля.
    await db_session.refresh(user, attribute_names=['jwt_tokens'])
    assert len(user.jwt_tokens) == 2

    await jwt_token_manager.remove_user_jwt_tokens(user.username)
    user = await user_manager.get_user_by_username(username)
    await db_session.refresh(user, attribute_names=['jwt_tokens'])
    assert len(user.jwt_tokens) == 0


@pytest.mark.asyncio
async def test_remove_expire_tokens(db_session: AsyncSession):
    """ Тестирует удаление просроченных JWT токенов """
    jwt_token_manger = JWTTokenManager(db_session)
    username: final = 'Paradox'

    await _add_jwt_token(db_session, -2, username)
    await _add_jwt_token(db_session, -1, username)
    jti = await _add_jwt_token(db_session, 1, username)

    # У пользователя должно быть три токена.
    assert await jwt_token_manger.get_user_jwt_token_count(username) == 3

    await jwt_token_manger.remove_expire_token()
    # У пользователя должен остаться один токен.
    assert await jwt_token_manger.get_user_jwt_token_count(username) == 1

    # Удаляется последний токен.
    await jwt_token_manger.remove_jwt_token(jti)
    assert await jwt_token_manger.get_user_jwt_token_count(username) == 0