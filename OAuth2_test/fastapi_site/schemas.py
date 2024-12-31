from datetime import datetime
from enum import StrEnum, IntEnum

from pydantic import BaseModel, ConfigDict
from starlette.authentication import SimpleUser, UnauthenticatedUser


class MyEnum(IntEnum):
    """ Собственный класс числовых перечислений. """
    @classmethod
    def get_name_for_value(cls, value):
        """ Возвращает название перечисления по его значению. """
        try:
            return [item.name for item in cls if item.value == value][0]
        except IndexError:
            return None

    @classmethod
    def get_names(cls):
        """ Возвращает кортеж всех наименований перечисления. """
        return tuple(val.name for val in cls)

    @classmethod
    def get_values(cls):
        """ Возвращает кортеж всех значений перечисления. """
        return tuple(val.value for val in cls)
    
    @classmethod
    def get_items(cls):
        """ Возвращает словарь всех наименований-значений перечисления. """
        return {item.name: item.value for item in cls}

class UerStatus(MyEnum):
    """ Перечисление статусов пользователей. """
    DELETED = 1
    BLOCKED = 2
    ACTIVE = 3
    

class UserRoles(MyEnum):
    """ Перечисление ролей пользователей. """
    system = 1
    super_admin = 2
    admin = 3
    admin_assistant = 4
    director = 5
    director_assistant = 6
    employee = 7
    visitor_vip = 8
    visitor = 9
    guest = 10


class JWTTokenType(StrEnum):
    """ Типы токенов """
    ACCESS  ='access'
    REFRESH = 'refresh'


class Token(BaseModel):
    """ Модель токена """
    access_token: str
    refresh_token: str
    token_type: str


class BaseUser(BaseModel):
    """ Базовая модель пользователя """
    username: str
    role: UserRoles
    status: UerStatus

    model_config = ConfigDict(from_attributes=True)

    def get_role(self):
        """ Возвращает название роли """
        return UserRoles.get_name_for_value(self.role)

    def __repr__(self) -> str:
        attrs = tuple(f"{field}={f'\'{value}\'' if isinstance(value, str) else value}" for field, value in self.model_dump().items())
        return f"{self.__class__.__name__}({', '.join(attrs)})"

class AnonymUser(BaseUser, UnauthenticatedUser):
    """ Анонимный пользователь. """
    username: str = 'Anonym'
    role: UserRoles = UserRoles.guest
    status: UerStatus = UerStatus.ACTIVE

class User(BaseUser, SimpleUser):
    """ Пользователь. """
    email: str | None
    first_name: str | None = None
    last_name: str | None = None
    date_joined: datetime
    last_login: datetime | None = None
