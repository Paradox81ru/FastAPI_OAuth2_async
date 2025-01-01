import uuid
from datetime import datetime, timedelta
from typing import final

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from Auth.db.models.jwt_token_manager import JWTTokenManager
from Auth.db.models.user_manager import UserManager
from config import Settings
from tests.conftest import db_session


class TestJwtToken:
    """ Тестирует работу с JWT токенами. """
    @classmethod
    async def _add_jwt_token(cls, db_session: AsyncSession, lifetime: int, username: str):
        """
        Добавляет данные о JWT токене.
        :param db_session: Сессия для работы с БД.
        :param lifetime: Время истечения срока токена в минутах.
        :param username: Имя пользователя, на которого выписывается токен.
        :return : Уникальный UUID код токена.
        :raises AssertionError:
        """
        jwt_token_manger = JWTTokenManager(db_session)
        jti = uuid.uuid4()
        data_expire = datetime.now() + timedelta(minutes=lifetime)
        await jwt_token_manger.add_jwt_token(jti, data_expire, username)
        assert await jwt_token_manger.has_jwt_token(jti)
        return jti

    @pytest.mark.asyncio
    async def test_jwt_token(self, db_session: AsyncSession, api_settings: Settings):
        """
        Тестирует создание, поиск и удаление JWT токенов.
        :param db_session:  Сессия для работы с БД.
        :param api_settings: Настройки приложения.
        :raises AssertionError:
        """
        jwt_token_manager = JWTTokenManager(db_session)
        user_manager = UserManager(db_session)
        username: final = api_settings.init_user_login

        jti = uuid.uuid4()
        assert not await jwt_token_manager.has_jwt_token(jti)

        await self._add_jwt_token(db_session, -1, username)
        jti = await self._add_jwt_token(db_session, -1, username)

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
        assert user is not None
        await db_session.refresh(user, attribute_names=['jwt_tokens'])
        assert len(user.jwt_tokens) == 0

    @pytest.mark.asyncio
    async def test_remove_expire_tokens(self, db_session: AsyncSession, api_settings: Settings):
        """
        Тестирует удаление просроченных JWT токенов.
        :param db_session:  Сессия для работы с БД.
        :param api_settings: Настройки приложения.
        :raises AssertionError:
        """
        jwt_token_manger = JWTTokenManager(db_session)
        username: final = api_settings.init_director_login

        jti_1 = await self._add_jwt_token(db_session, -2, username)
        jti_2 = await self._add_jwt_token(db_session, -1, username)
        jti_3 = await self._add_jwt_token(db_session, 1, username)

        # У пользователя должно быть три токена.
        assert await jwt_token_manger.get_user_jwt_token_count(username) == 3
        # Достаются все токена пользователя,
        tokens_username = await jwt_token_manger.get_user_jwt_tokens(username)
        # и проверяется, что они являются токенами, созданные немного ранее.
        jti_list = map(lambda x: x.jti, tokens_username)
        assert all(map(lambda x: x in jti_list, (jti_1, jti_2, jti_3)))

        await jwt_token_manger.remove_expire_token()
        # У пользователя должен остаться один токен.
        assert await jwt_token_manger.get_user_jwt_token_count(username) == 1

        # Удаляется последний токен.
        await jwt_token_manger.remove_jwt_token(jti_3)
        assert await jwt_token_manger.get_user_jwt_token_count(username) == 0

    @pytest.mark.asyncio
    async def test_create_access_and_refresh_token(self, db_session: AsyncSession, api_settings: Settings):
        jwt_token_manager = JWTTokenManager(db_session)
        username: final = api_settings.init_user_login

        # Проверка, что у пользователя ещё нет токенов.
        assert await jwt_token_manager.get_user_jwt_token_count(username) == 0
        # Пользователю создаётся токен доступа.
        await jwt_token_manager.create_access_token(username, {})
        assert await jwt_token_manager.get_user_jwt_token_count(username) == 1

        # Пользователю создаётся токен обновления.
        await jwt_token_manager.create_refresh_token(username, {})
        assert await jwt_token_manager.get_user_jwt_token_count(username) == 2


