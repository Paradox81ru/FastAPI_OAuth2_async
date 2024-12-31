from datetime import datetime

from Auth.db.models import Base
from sqlalchemy import String, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config import get_pwd_context
from Auth.schemas import UserRoles, UerStatus
from Auth.db.db_types import MyDateTime


class User(Base):
    """ Пользователь. """
    __tablename__ = 'accounts_user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(60), default="")
    last_name: Mapped[str | None] = mapped_column(String(60), default="")
    email: Mapped[str] = mapped_column(String(254))
    status: Mapped[UerStatus] = mapped_column(SMALLINT)
    role: Mapped[UserRoles] = mapped_column(SMALLINT)
    date_joined: Mapped[datetime] = mapped_column(MyDateTime, default=datetime.now)
    last_login: Mapped[datetime | None] = mapped_column(MyDateTime)
    jwt_tokens: Mapped[list['JWTToken']] = relationship(back_populates='subject', cascade="all, delete-orphan")

    def set_password(self, password: str):
        """ Устанавливает пользователю пароль. """
        self.password_hash = get_pwd_context().hash(password)


class UserBuilder:
    """ Класс создатель пользователя. """

    def __init__(self, username: str, email: str) -> None:
        """
        Конструктор класса.
        :param username: Логин пользователя.
        :param email: Электронная почта пользователя.
        """
        self._user = User(username=username, email=email)

    def name(self, first_name='', last_name=''):
        """
        Добавляет имя и фамилию. Если пропустить этот шаг,
        то по умолчанию будут установлены значения пустые строки.
        :param first_name: Имя пользователя.
        :param last_name: Фамилия пользователя.
        :return: Класс создателя пользователя.
        """
        self._user.first_name = first_name
        self._user.last_name = last_name
        return self

    def role(self, role: UserRoles):
        """
        Добавляет роль пользователя.
        Если пропустить это шаг, то по умолчанию будет установлена роль посетителя.
        :return: Класс создателя пользователя.
        """
        self._user.role = role
        return self

    def set_password(self, password):
        """
        Устанавливает пароль пользователя.
        Если пропустить этот шаг, то после создания пользователя будет вызвано исключение
        AttributeError("The password field is not set").
        :return: Класс создателя пользователя.
        """
        self._user.set_password(password)
        return self

    def build(self):
        """
        По ввёдённым ранее параметрам создаёт пользователя.
        :return: Пользователь.
        :raises AttributeError: Значение пароля не установлено.
        """
        if self._user.password_hash is None:
            raise AttributeError("The password field is not set")
        if self._user.role is None:
            self.role(UserRoles.visitor)
        self._user.status = UerStatus.ACTIVE
        self._user.date_joined = datetime.now()
        return self._user
