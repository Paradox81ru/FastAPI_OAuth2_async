import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from Auth.schemas import UserRoles
from tests.conftest import UserType, get_access_token


def get_headers(token):
    """ Возвращает заголовок для авторизации по токену. """
    return {'Authorization': f"Bearer {token}"}


class TestScopeMe:
    """ Тестирует api 'api/test/scope/me' - авторизация со scope 'me'. """
    @classmethod
    def setup_class(cls):
        """ Инициализирует тест. """
        cls.api = "/api/test/scope/me"

    async def test_scope_me(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me' для пользователя авторизовавшегося со scope 'me'.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = await get_access_token(async_client, user_auth, ['me'])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name, 'scopes': ['me']}

    async def test_scope_me_and_items(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me' для пользователя авторизовавшегося со scope 'me' и 'items'.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, ['me', 'items'])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.director.name, 'scopes': ['me', 'items']}

    async def test_note_scope_me(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me' для пользователя авторизовавшегося только со scope 'items', но без scope 'me'.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, ['items'])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    async def test_without_scope(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me' для пользователя авторизовавшегося без установленного scope.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'


class TestScopeMeItems:
    """ Тестирует api 'api/test/scope/me_items' - авторизация со scope 'me' и 'items'. """

    @classmethod
    def setup_class(cls):
        """ Инициализирует тест. """
        cls.api = "/api/test/scope/me_items"

    async def test_scope_me_and_items(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me_items' для пользователя авторизовавшегося со scope 'me'.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = await get_access_token(async_client, user_auth, ['me', 'items'])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name, 'scopes': ['me', 'items']}

    async def test_scope_me(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me_items' для пользователя авторизовавшегося только со scope 'me', но без scope 'items'/
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, ['me'])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    async def test_scope_items(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me_items' для пользователя авторизовавшегося только со scope 'items', но без scope 'me'.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, ['items'])

        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'

    async def test_without_scope(self, async_client: AsyncClient, users_data):
        """
        Поверяет 'api/scope/me_items' для пользователя авторизовавшегося без установленного scope.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, [])

        response = await async_client.get(self.api, headers=get_headers(token))
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
                         ids=[f"Checks the 'only_{arg[0]}' by the {arg[1]} user" for arg in role_args])
async def test_role(async_client: AsyncClient, users_data, only_role: str, user_type: UserType, role_name: str | None):
    """
    Проверяет аутентификацию по роли.
    :param async_client: Асинхронный тестовый клиент.
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
        token = await get_access_token(async_client, user_auth, [])
        headers = get_headers(token)
    else:
        # Для анонимного пользователя указывать токен в заголовке не надо
        headers = {}
    response = await async_client.get(api, headers=headers)
    if role_name is not None:
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': role_name}
    else:
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not enough permissions'


class TestOnlyAuthorizedUser:
    """ Тестирует api '/api/test/only_authorized_user' - только авторизованный пользователь. """

    @classmethod
    def setup_class(cls):
        """ Инициализирует тест. """
        cls.api = "/api/test/only_authorized_user"

    async def test_admin(self, async_client: AsyncClient, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Администратор.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.ADMIN]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.admin.name}

    async def test_director(self, async_client: AsyncClient, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Директор.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.director.name}

    async def test_user(self, async_client: AsyncClient, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с обычным пользователем.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'username': user_auth.username,
                                   'role': UserRoles.visitor.name}

    async def test_not_authorized(self, async_client: AsyncClient):
        """
        Тестирует api '/api/test/only_authorized_user' - без авторизации.
        :param async_client: Асинхронный тестовый клиент.
        :raises AssertionError:
        """
        response = await async_client.get(self.api)
        assert response.status_code == 401
        assert response.json()['detail'] == 'Not authorized'


class TestOnlyAnonymUser:
    """ Тестирует api '/api/test/only_authorized_user' - только авторизованный пользователь. """

    @classmethod
    def setup_class(cls):
        """ Инициализирует тест. """
        cls.api = "/api/test/only_anonym_user"

    async def test_not_authorized(self, async_client: AsyncClient):
        """
        Тестирует api '/api/test/only_authorized_user' - без авторизации.
        :param async_client: Асинхронный тестовый клиент.
        :raises AssertionError:
        """
        response = await async_client.get(self.api)
        assert response.json() == {'status': 'ok', 'username': 'Anonym',
                                   'role': UserRoles.guest.name}

    async def test_admin(self, async_client: AsyncClient, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Администратор.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.ADMIN]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.admin.name}")

    async def test_director(self, async_client: AsyncClient,  users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с пользователем Директор.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.DIRECTOR]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.director.name}")

    async def test_user(self, async_client: AsyncClient, users_data):
        """
        Тестирует api '/api/test/only_authorized_user' - с обычным пользователем.
        :param async_client: Асинхронный тестовый клиент.
        :param users_data: Данные для авторизации пользователя (логин и пароль).
        :raises AssertionError:
        """
        user_auth = users_data[UserType.USER]
        token = await get_access_token(async_client, user_auth, [])
        response = await async_client.get(self.api, headers=get_headers(token))
        assert response.status_code == 401
        assert (response.json()['detail'] ==
                f"Already authorized username '{user_auth.username}' role {UserRoles.visitor.name}")
