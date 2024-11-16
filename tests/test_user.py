import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from OAuth2.db import models
from OAuth2.db.models.user import UserBuilder
from OAuth2.db.models.user_manager import UserManager
from OAuth2 import schemas
from OAuth2.schemas import UserRoles, UerStatus
from OAuth2.config import get_settings

settings = get_settings()
# pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_existence_original_users(db_session: AsyncSession):
    """ Проверяет наличие первоначальных пользователей """
    user_manager = UserManager(db_session)
    stmt = select(func.count(models.User.id))
    user_count = (await db_session.execute(stmt)).scalar_one()
    assert user_count == 4

    admin_user = await user_manager.get_user_by_username('Admin')
    assert admin_user.username == 'Admin'
    assert admin_user.role == UserRoles.admin
    assert admin_user.status == UerStatus.ACTIVE
    print(f"Admin user_model: {repr(admin_user)}")   
    admin_user_schema = schemas.UserInDB(**admin_user.to_dict())
    print(f"Admin user_schema: {repr(admin_user_schema)}")
    assert not admin_user_schema.check_password("qwerty")
    assert admin_user_schema.check_password(settings.init_admin_password.get_secret_value())

    system_user = await user_manager.get_user_by_username('System')
    assert system_user.username == "System"
    assert system_user.role == UserRoles.system
    assert system_user.status == UerStatus.ACTIVE
    system_user_schema = schemas.UserInDB(**system_user.to_dict())
    assert not system_user_schema.check_password("qwerty")
    assert system_user_schema.check_password(settings.init_system_password.get_secret_value())

    director_user = await user_manager.get_user_by_username('Paradox')
    assert director_user.username == 'Paradox'
    assert director_user.role == UserRoles.director
    assert director_user.status == UerStatus.ACTIVE
    director_user_schema = schemas.UserInDB(**director_user.to_dict())
    assert not director_user_schema.check_password("qwerty")
    assert director_user_schema.check_password(settings.init_director_password.get_secret_value())

    user = await user_manager.get_user_by_username('User')
    assert user.username == 'User'
    assert user.role == UserRoles.visitor
    assert user.status == UerStatus.ACTIVE
    user_schema = schemas.UserInDB(**user.to_dict())
    assert not user_schema.check_password("qwerty")
    assert user_schema.check_password(settings.init_user_password.get_secret_value())

    unknown_user = await user_manager.get_user_by_username('Unknown')
    print(f"Unknown user: {unknown_user}")


@pytest.mark.asyncio
async def test_add_user(db_session: AsyncSession):
    user_manager = UserManager(db_session)
    new_user = UserBuilder('NewUser', 'new_user@mail.ru').set_password("qwerty").build()
    assert new_user.username == 'NewUser'
    assert new_user.email == 'new_user@mail.ru'
    assert new_user.role == UserRoles.visitor
    assert new_user.status == UerStatus.ACTIVE
    user_manager.add_user(new_user)

    find_new_user = await user_manager.get_user_by_username('NewUser')
    assert find_new_user.username == 'NewUser'
    assert find_new_user.email == 'new_user@mail.ru'
    assert find_new_user.role == UserRoles.visitor
    assert find_new_user.status == UerStatus.ACTIVE


@pytest.mark.asyncio
async def test_set_password(db_session: AsyncSession):
    user_manager = UserManager(db_session)
    password = 'qwerty'
    user_model = UserBuilder("NewUser", "new_user@mail.ru").set_password(password).build()
    user_schema = schemas.UserInDB(**user_model.to_dict())
    assert user_schema.check_password(password)

    password = 'Cucumber_123'
    paradox = await user_manager.get_user_schema_by_username('Paradox')
    assert paradox.check_password(password)
    password = 'cucumber_123'
    assert not paradox.check_password(password)


@pytest.mark.asyncio
async def test_convert_userdb_to_user(db_session: AsyncSession):
    user_manager = UserManager(db_session)
    paradox_in_db = await user_manager.get_user_schema_by_username('Paradox')
    paradox = paradox_in_db.to_user()
    assert isinstance(paradox, schemas.User)