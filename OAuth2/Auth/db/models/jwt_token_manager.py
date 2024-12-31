import uuid
from datetime import datetime, timezone, timedelta
from uuid import UUID

import jwt
from sqlalchemy import select, func, delete

from config import get_settings
from Auth.db.models import User, JWTToken
from Auth.db.models.base import BaseManager
from Auth.schemas import JWTTokenType

settings = get_settings()


class JWTTokenManager(BaseManager):
    """ Менеджер JWT токенов (singleton). """

    async def create_access_token(self, username: str, data: dict) -> str:
        """
        Создаёт токен доступа.
        :param username: Имя пользователя, на которого выписывается токен доступа.
        :param data: Словарь с данными, которые нужно добавить в токен доступа.
        :return : Токен доступа.
        """
        token_expire = timedelta(minutes=settings.access_token_expire_minutes)
        jti, expire, token = self._sign_token(JWTTokenType.ACCESS, username, data, token_expire)
        await self.add_jwt_token(jti, expire, username)
        return token

    async def create_refresh_token(self, username, data: dict) -> str:
        """
        Создаёт токен обновления.
        :param username: Имя пользователя, на которого выписывается токен обновления.
        :param data: Словарь с данными, которые нужно добавить в токен обновления.
        :return: Токен обновления.
        """
        token_expire = timedelta(minutes=settings.refresh_token_expire_minutes)
        jti, expire, token = self._sign_token(JWTTokenType.REFRESH, username, data, token_expire)
        await self.add_jwt_token(jti, expire, username)
        return token

    async def add_jwt_token(self, jti: UUID, data_expire: datetime, username: str):
        """
        Добавляет JWT токен для пользователя.
        :param jti: Уникальный идентификатор в формате UUID.
        :param data_expire: Время истечения токена.
        :param username: Логин пользователя, владельца токена.
        """
        # user = self._db.query(User).filter(User.username == username).one()
        user = (await self._db_async.scalars(select(User).where(User.username == username))).one()
        token = JWTToken(jti=jti, subject=user, expire=data_expire)
        self._db_async.add(token)
        await self._db_async.commit()

    async def get_jwt_token(self, jti: UUID | str):
        """ Возвращает JWT токен по его jti """
        jti = UUID(jti) if isinstance(jti, str) else jti
        # return self._db.query(JWTToken).filter(JWTToken.jti == jti).one_or_none()
        return (await self._db_async.scalars(select(JWTToken).where(JWTToken.jti == jti))).one_or_none()

    async def has_jwt_token(self, jti: UUID | str) -> bool:
        """ Проверяет, существует ли указанный JWT токен """
        result = await self.get_jwt_token(jti)
        return result is not None

    async def get_user_jwt_tokens(self, username: str):
        """ Возвращает все токены указанного пользователя. """
        return (await self._db_async.scalars(select(JWTToken).join(JWTToken.subject).where(User.username == username))).all()
        # return self._db.query(JWTToken).join(User).where(User.username == username).all()

    async def get_user_jwt_token_count(self, username: str):
        """ Возвращает количество токенов у указанного пользователя """
        return (await self._db_async.scalar(select(func.count(JWTToken.jti)).join(User).where(
            User.username == username)))
        # return self._db.execute(select(func.count(JWTToken.jti)).join(User).where(
        #     User.username == username)).scalar_one()

    async def remove_jwt_token(self, jti: UUID | str):
        """ Удаляет JWT токен по его UUID """
        jti = UUID(jti) if isinstance(jti, str) else jti
        # db.execute(delete(models.JWTToken).where(models.JWTToken.jti == jti))
        # self._db.query(JWTToken).where(JWTToken.jti == jti).delete(synchronize_session='fetch')
        await self._db_async.execute(delete(JWTToken).where(JWTToken.jti == jti))
        await self._db_async.commit()

    async def remove_user_jwt_tokens(self, username: str):
        """ Удаляет все токены для указанного пользователя """
        # noinspection PyTypeChecker
        user: User = (await self._db_async.scalars(select(User).filter(User.username == username))).one()
        user.jwt_tokens.clear()
        await self._db_async.commit()

    async def remove_expire_token(self):
        """ Удаляет все истёкшие токены """
        # db.execute(delete(models.JWTToken).where(models.JWTToken.expire < datetime.now()))
        # db.query(models.JWTToken).where(models.JWTToken.expire < datetime.now()).delete(synchronize_session='fetch')

        # expire_tokens = self._db.query(JWTToken).filter(JWTToken.expire < datetime.now())
        # for token in expire_tokens:
        #     self._db.delete(token)
        # self._db.commit()
        expire_tokens = (await self._db_async.scalars(select(JWTToken).filter(JWTToken.expire < datetime.now())))
        for token in expire_tokens:
            await self._db_async.delete(token)
        await self._db_async.commit()

    @classmethod
    def _sign_token(cls, _type: JWTTokenType, subject: str, data: dict[str, any],
                    expires_delta: timedelta | None = None) -> tuple[UUID, datetime, str]:
        """
        Создаёт JWT токен.
        :param _type: Тип токена(access/refresh).
        :param subject: Субъект, на которого выписывается токен.
        :param data: Информация добавляемая в токен.
        :param expires_delta: Время жизни токена.
        :return : Кортеж, где первое значение - uuid номер в формате UUID,
                              второе значение - дата истечения срока токена,
                              а третье значение это сам JWT токен в формате строки.
        """
        payload = data.copy()
        date_now = datetime.now(timezone.utc)
        expire = (payload['nbf'] if 'nbf' in payload else date_now) + (
            expires_delta if expires_delta is not None else timedelta(minutes=15))
        jti = uuid.uuid4()

        _data = {'iss': "paradox81ru@mail.ru",
                 'sub': subject,
                 'type': _type,
                 'jti': str(jti),
                 'iat': date_now,
                 'nbf': payload['nbf'] if 'nbf' in payload else date_now,
                 'exp': expire
                 }
        payload.update(_data)
        encode_jwt = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm="HS256")
        return jti, expire, encode_jwt
