from sqlalchemy.orm import Session

from OAuth2.config import get_settings
from OAuth2.db.models.user import UserBuilder
from OAuth2.db.models.user_manager import UserManager
from OAuth2.schemas import UserRoles

settings = get_settings()


def init_users(db: Session):
    """ Добавление пользователей при первой инициализации базы данных """
    user_manager = UserManager(db)
    user_admin = UserBuilder('Admin', 'paradox81ru@yandex.ru').role(UserRoles.admin).set_password(settings.init_admin_password.get_secret_value()).build()
    user_system = UserBuilder('System', 'paradox81ru@gmail.com').role(UserRoles.system).set_password(settings.init_system_password.get_secret_value()).build()
    user_paradox = UserBuilder('Paradox', 'paradox81ru@mail.ru').name("Жорж", "Парадокс") \
                                .role(UserRoles.director).set_password(settings.init_director_password.get_secret_value()).build()
    user_user = UserBuilder("User", 'paradox81ru@hotmail.com').name('Пользователь').set_password(settings.init_user_password.get_secret_value()).build()
    users = [user_admin, user_system, user_paradox, user_user]
    user_manager.add_users(users)
