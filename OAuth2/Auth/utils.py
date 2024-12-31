from sqlalchemy.orm import Session
# from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from Auth.db.models.user import UserBuilder
from Auth.db.models.user_manager import UserManager
from Auth.schemas import UserRoles

settings = get_settings()


def init_users(db: Session):
    """
    Добавление пользователей при первой инициализации базы данных
    :param db: Сессия для работы с базой данных.
    """
    user_manager = UserManager(db=db)
    user_admin = (UserBuilder('Admin', settings.init_admin_email).role(UserRoles.admin)
                  .set_password(settings.init_admin_password.get_secret_value()).build())
    user_system = (UserBuilder('System', settings.init_system_email).role(UserRoles.system)
                   .set_password(settings.init_system_password.get_secret_value()).build())
    user_paradox = (UserBuilder(settings.init_director_login, settings.init_director_email)
                    .name(settings.init_director_name, settings.init_director_lastname)
                    .role(UserRoles.director).set_password(settings.init_director_password.get_secret_value()).build())
    user_user = (UserBuilder(settings.init_user_login, settings.init_user_email)
                 .name(settings.init_user_name, settings.init_user_lastname)
                 .set_password(settings.init_user_password.get_secret_value()).build())
    users = [user_admin, user_system, user_paradox, user_user]
    user_manager.add_users(users)
