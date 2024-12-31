import pytest
from fastapi.testclient import TestClient

from fastapi_site.schemas import UserRoles
from tests.conftest import get_access_token, UserType

""" 
!!!!                                                ВАЖНО                                                       !!!! 
!!!! Для работы данных тестов требуется, чтобы был запущен сервер авторизации. Причем надо учитывать,           !!!! 
!!!! что при запуске сервера авторизации, он запускается не с тестовыми параметрами, а с рабочими,              !!!! 
!!!! поэтому логины и пароли проверяются из рабочей базы. Соответственно в conftest-е Oauth2Settings настройки  !!!! 
!!!! загружаются не из tests/.env, а из Auth/.env.                                                              !!!!
"""


def get_headers(token):
    """ Возвращает заголовок для авторизации по токену. """
    return {'Authorization': f"Bearer {token}"}


class TestScopeMe:
    """ Тестирует api 'api/test/scope/me' - авторизация со scope 'me'. """
    @classmethod
    def setup_class(cls):
        """ Настройка теста. """
        cls.api = "/api/test/scope/me"

    def test_scope_me(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me' для пользователя авторизовавшегося со scope 'me'.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = get_access_token(user_auth, oauth_server, ['me'])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name, 'scopes': ['me']}

    def test_scope_me_and_items(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me' для пользователя авторизовавшегося со scope 'me' и 'items'.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, ['me', 'items'])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.director.name, 'scopes': ['me', 'items']}

    def test_note_scope_me(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me' для пользователя авторизовавшегося только со scope 'items', но без scope 'me'.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, ['items'])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    def test_without_scope(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me' для пользователя авторизовавшегося без установленного scope.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'


class TestScopeMeItems:
    """ Тестирует api 'api/test/scope/me_items' - авторизация со scope 'me' и 'items'. """
    @classmethod
    def setup_class(cls):
        """ Настройка теста. """
        cls.api = "/api/test/scope/me_items"

    def test_scope_me_and_items(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me_items' для пользователя авторизовавшегося со scope 'me'
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = get_access_token(user_auth, oauth_server, ['me', 'items'])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name, 'scopes': ['me', 'items']}

    def test_scope_me(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me_items' для пользователя авторизовавшегося только со scope 'me', но без scope 'items'.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, ['me'])

        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    def test_scope_items(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me_items' для пользователя авторизовавшегося только со scope 'items', но без scope 'me'.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, ['items'])

        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    def test_without_scope(self, client: TestClient, oauth_server, users_data):
        """
        Проверяет 'api/scope/me_items' для пользователя авторизовавшегося без установленного scope
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, [])

        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'


# Параметры для теста 'test_role'.
role_args = (
    ['admin', UserType.ADMIN, UserRoles.admin.name],
    ['admin', UserType.DIRECTOR, None],
    ['admin', UserType.USER, None],
    ['admin', UserType.ANONYM, None],
    ['director', UserType.DIRECTOR, UserRoles.director.name],
    ['director', UserType.ADMIN, None],
    ['director', UserType.USER, None],
    ['director', UserType.ANONYM, None],
    ['admin_or_director', UserType.ADMIN, UserRoles.admin.name],
    ['admin_or_director', UserType.DIRECTOR, UserRoles.director.name],
    ['admin_or_director', UserType.USER, None],
    ['admin_or_director', UserType.ANONYM, None],
    ['user', UserType.USER, UserRoles.visitor.name],
    ['user', UserType.ADMIN, None],
    ['user', UserType.DIRECTOR, None],
    ['user', UserType.ANONYM, None],
)


@pytest.mark.parametrize('only_role, user_type, role_name', role_args,
                         ids=[f"Checks the 'only_{arg[0]}' by the {arg[1]} user"  for arg in role_args])
def test_role(client: TestClient, oauth_server, users_data,
              only_role: str, user_type: UserType, role_name: str | None):
    """
    Проверяет аутентификацию по роли.
    :param client:Тестовый клиент.
    :param oauth_server: Сервер авторизации.
    :param users_data: Данные для авторизации пользователя (логин и пароль).
    :param only_role: Тип аутентификации.
    :param user_type: Авторизующийся пользователь.
    :param role_name: Роль авторизующегося пользователя. Если None, то доступ этому пользователю запрещён.
    :raises AssertionError:
    """
    api = f"/api/test/only_{only_role}"
    user_auth = ""
    if user_type != UserType.ANONYM:
        user_auth = users_data[user_type]
        token = get_access_token(user_auth, oauth_server, [])
        headers = get_headers(token)
    else:
        # Для анонимного пользователя указывать токен в заголовке не надо
        headers = {}
    response = client.get(api, headers=headers)
    if role_name is not None:
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': role_name}
    else:
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'


class TestOnlyAuthorizedUser:
    """ Тестирует api '/api/test/only_authorized_user' - только авторизованный пользователь """

    @classmethod
    def setup_class(cls):
        """ Настройка теста. """
        cls.api = "/api/test/only_authorized_user"

    def test_admin(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Администратор.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.ADMIN]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.admin.name}

    def test_director(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Директор.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.director.name}

    def test_user(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с обычным пользователем.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name}

    def test_not_authorized(self, client: TestClient):
        """
        Тестирует api '/api/test/only_authorized_user' - без авторизации.
        :param client: Тестовый клиент.
        :raises AssertionError:
        """
        response = client.get(self.api)
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not authorized'


class TestOnlyAnonymUser:
    """ Тестирует api '/api/test/only_authorized_user' - только авторизованный пользователь. """

    @classmethod
    def setup_class(cls):
        """ Настройка теста. """
        cls.api = "/api/test/only_anonym_user"

    def test_not_authorized(self, client: TestClient):
        """
        Тестирует api '/api/test/only_authorized_user' - без авторизации.
        :param client: Тестовый клиент.
        :raises AssertionError:
        """

        response = client.get(self.api)
        assert response.json() == {'status': 'ok', 'username': 'Anonym',
                                   'role': UserRoles.guest.name}

    def test_admin(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Администратор.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.ADMIN]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.admin.name}")

    def test_director(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Директор.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.director.name}")

    def test_user(self, client: TestClient, oauth_server, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с обычным пользователем.
        :param client: Тестовый клиент.
        :param oauth_server: URL сервера авторизации.
        :param users_data: Данные для авторизации пользователя по типу пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = get_access_token(user_auth, oauth_server, [])
        response = client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.visitor.name}")
