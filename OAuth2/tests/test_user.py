import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from Auth.db import models
from Auth.db.models.user import UserBuilder
from Auth.db.models.user_manager import UserManager
from Auth import schemas
from Auth.schemas import UserRoles, UerStatus
from config import Settings


class TestUser:
    """ Тестирует работу с пользователями. """

    @pytest.mark.asyncio
    async def test_existence_original_users(self, db_session: AsyncSession, api_settings: Settings):
        """
        Проверяет наличие первоначальных пользователей.
        :param db_session: Сессия для работы с базой данных.
        :param api_settings: Настройки приложения.
        :raises AssertionError:
        """
        user_manager = UserManager(db_session)
        stmt = select(func.count(models.User.id))
        user_count = (await db_session.execute(stmt)).scalar_one()
        assert user_count == 4

        # Проверка наличия администратора.
        admin_user = await user_manager.get_user_by_username('Admin')
        assert admin_user.username == 'Admin'
        assert admin_user.role == UserRoles.admin
        assert admin_user.status == UerStatus.ACTIVE
        print(f"Admin user_model: {repr(admin_user)}")
        admin_user_schema = schemas.UserInDB(**admin_user.to_dict())
        print(f"Admin user_schema: {repr(admin_user_schema)}")
        assert not admin_user_schema.check_password("qwerty")
        assert admin_user_schema.check_password(api_settings.init_admin_password.get_secret_value())

        # Проверка наличия системного пользователя.
        system_user = await user_manager.get_user_by_username('System')
        assert system_user.username == "System"
        assert system_user.role == UserRoles.system
        assert system_user.status == UerStatus.ACTIVE
        system_user_schema = schemas.UserInDB(**system_user.to_dict())
        assert not system_user_schema.check_password("qwerty")
        assert system_user_schema.check_password(api_settings.init_system_password.get_secret_value())

        # Проверка наличия пользователя с правами директора.
        director_user = await user_manager.get_user_by_username(api_settings.init_director_login)
        assert director_user.username == api_settings.init_director_login
        assert director_user.first_name == api_settings.init_director_name
        assert director_user.last_name == api_settings.init_director_lastname
        assert director_user.email == api_settings.init_director_email
        assert director_user.role == UserRoles.director
        assert director_user.status == UerStatus.ACTIVE
        director_user_schema = schemas.UserInDB(**director_user.to_dict())
        assert not director_user_schema.check_password("qwerty")
        assert director_user_schema.check_password(api_settings.init_director_password.get_secret_value())

        # Проверка наличия обычного пользователя с правами посетителя.
        user = await user_manager.get_user_by_username(api_settings.init_user_login)
        assert user.username == api_settings.init_user_login
        assert user.first_name == api_settings.init_user_name
        assert user.last_name == api_settings.init_user_lastname
        assert user.email == api_settings.init_user_email
        assert user.role == UserRoles.visitor
        assert user.status == UerStatus.ACTIVE
        user_schema = schemas.UserInDB(**user.to_dict())
        assert not user_schema.check_password("qwerty")
        assert user_schema.check_password(api_settings.init_user_password.get_secret_value())

        # Проверка возврата None при отсутствии искомого пользователя.
        unknown_user = await user_manager.get_user_by_username('Unknown')
        assert unknown_user is None

    @pytest.mark.asyncio
    async def test_add_user(self, db_session: AsyncSession):
        """
        Проверяет создание пользователей.
        :param db_session: Сессия для работы с базой данных.
        :raises AssertionError:
        """
        user_manager = UserManager(db_session)
        new_user = UserBuilder('NewUser', 'new_user@mail.ru').set_password("qwerty").build()
        assert new_user.username == 'NewUser'
        assert new_user.email == 'new_user@mail.ru'
        assert new_user.role == UserRoles.visitor
        assert new_user.status == UerStatus.ACTIVE

        await user_manager.add_user(new_user)
        find_new_user = await user_manager.get_user_by_username('NewUser')
        assert find_new_user.username == 'NewUser'
        assert find_new_user.email == 'new_user@mail.ru'
        assert find_new_user.role == UserRoles.visitor
        assert find_new_user.status == UerStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_set_password(self, db_session: AsyncSession, api_settings: Settings):
        """
        Проверяет установку пользователям паролей.
        :param db_session: Сессия для работы с базой данных.
        :param api_settings: Настройки приложения.
        :raises AssertionError:
        """
        user_manager = UserManager(db_session)
        password = 'qwerty'
        user_model = UserBuilder("NewUser", "new_user@mail.ru").set_password(password).build()
        user_schema = schemas.UserInDB(**user_model.to_dict())
        assert user_schema.check_password(password)

        password = api_settings.init_director_password.get_secret_value()
        director = await user_manager.get_user_schema_by_username(api_settings.init_director_login)
        assert director.check_password(password)
        password = password + "_"
        assert not director.check_password(password)

    @pytest.mark.asyncio
    async def test_convert_userdb_to_user(self, db_session: AsyncSession, api_settings: Settings):
        """
        Проверяет конвертацию пользователя из AlchemySQL в FastAPI модель.
        :param db_session: Сессия для работы с базой данных.
        :param api_settings: Настройки приложения.
        :raises AssertionError:
        """
        user_manager = UserManager(db_session)
        paradox_in_db = await user_manager.get_user_schema_by_username(api_settings.init_director_login)
        paradox = paradox_in_db.to_user()
        assert isinstance(paradox, schemas.User)
