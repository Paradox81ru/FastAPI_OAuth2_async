from uuid import UUID
from typing import cast

from sqlalchemy import select

from Auth import schemas
from Auth.db.models import User, JWTToken
from Auth.db.models.base import BaseManager


class UserManager(BaseManager):
    """ Менеджер пользователей (singleton). """
    async def get_user_by_username(self, username) -> User | None:
        """ Возвращает пользователя по логину """
        return (await self._db_async.scalars(select(User).where(User.username == username)
                                             # .options(selectinload(User.jwt_tokens))
                                             )).first()
        # return self._a_db.query(User).filter(User.username == username).first()

    async def get_user_schema_by_username(self, username) -> schemas.UserInDB | None:
        """ Возвращает найденного по логину пользователя"""
        user = await self.get_user_by_username(username)
        return schemas.UserInDB(**user.to_dict()) if user is not None else None

    async def get_authenticate_user(self, username: str, password: str):
        """ Возвращает авторизованного пользователя. """
        user = await self.get_user_schema_by_username(username)
        if user is None or not user.check_password(password):
            return False
        return user.to_user()

    async def get_user_by_jwt_token(self, jti: UUID | str) -> User:
        """ Возвращает пользователя по JTI токена """
        jti = UUID(jti) if isinstance(jti, str) else jti
        # 'options(selectinload(User.jwt_tokens))' нужно для одновременной загрузки данных о токенах,
        # для возможности асинхронного доступа к связанному полю
        return cast(User, (await self._db_async.scalars(select(User).join(User.jwt_tokens).where(JWTToken.jti == jti)
                                                        # .options(selectinload(User.jwt_tokens))
                                                        )).one())
        # return cast(User, self._db.query(User).join(User.jwt_tokens).filter( JWTToken.jti == jti).one())
        # return db.query(User).filter(User.jwt_tokens.contains(
        #     db.query(JWTToken).filter(JWTToken.jti == jti))).first()

    async def add_user(self, user: User):
        """ Добавляет пользователя. """
        self._db_async.add(user)
        await self._db_async.commit()

    def add_users(self, users: list[User]):
        """ Добавляет список пользователей. """
        self._db.add_all(users)
        self._db.commit()
