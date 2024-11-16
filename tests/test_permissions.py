from fastapi import Response
from fastapi.testclient import TestClient
from OAuth2.config import Settings


def get_token_headers(response_json):
    """ Возвращает заголовок авторизованного пользователя """
    return {'Authorization': f"Bearer {response_json['access_token']}"}


def get_user_data(user, api_settings: Settings):
    """ Возвращает данные для авторизации пользователя """
    get_password = {
        'Admin': api_settings.init_admin_password.get_secret_value,
        'Paradox': api_settings.init_director_password.get_secret_value,
        'User': api_settings.init_user_password.get_secret_value
    }
    return {"username": user, 'password': get_password[user]()}


def get_response_admin_json(client: TestClient, api_settings):
    """ Возвращает JSON ответ запрашиваемого токена для администратора """
    response = client.post("/api/oauth/token", data={"username": 'Admin', 'password': api_settings.init_admin_password.get_secret_value()})
    return get_response_json(response)


def get_response_director_json(client: TestClient, api_settings):
    """ Возвращает JSON ответ запрашиваемого токена для директора """
    response = client.post("/api/oauth/token", data=get_user_data('Paradox', api_settings))
    return get_response_json(response)


def get_response_user_json(client: TestClient, api_settings):
    """ Возвращает JSON ответ запрашиваемого токена для пользователя """
    response = client.post("/api/oauth/token", data=get_user_data('User', api_settings))
    return get_response_json(response)


def get_response_json(response: Response):
    """ Возвращает JSON ответ """
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['token_type'] == 'bearer'
    return response_json


def test_admin_roles(client: TestClient, api_settings):
    """ Проверяет роль администратора """
    # Только для админа без авторизации
    response = client.get("/api/test/only_admin")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not enough permissions"}

    # Запрос токена для админа с неправильным паролем.
    response = client.post("/api/oauth/token", data={"username": 'Admin', 'password': "qwerty"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}

    # Запрос токена на админа
    response_admin_json = get_response_admin_json(client, api_settings)

    # Только для админ с авторизацией
    response = client.get("/api/test/only_admin", headers={'Authorization': f"Bearer {response_admin_json['access_token']}"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "role": "admin" }

    # Только для директора с авторизацей
    response = client.get("/api/test/only_director", headers=get_token_headers(response_admin_json))
    assert response.status_code == 401
    assert response.json() == {"detail": "Not enough permissions"}


def test_authorized_user(client: TestClient, api_settings):
    """ Проверят только авторизованного пользователя """
    # Только авторизованный пользователь без авторизации
    response = client.get("/api/test/authorized_user")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authorized"}

    # Запрос токена на директора
    response_director_json = get_response_director_json(client, api_settings)

    # Только авторизованный пользователь директором
    response = client.get("/api/test/authorized_user", headers=get_token_headers(response_director_json))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "username": "Paradox",  "role": "director" }

    # Запрос токена на пользователя
    response_user_json = get_response_user_json(client, api_settings)

    # Только авторизованный пользователь пользователем
    response = client.get("/api/test/authorized_user", headers=get_token_headers(response_user_json))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "username": "User",  "role": "visitor" }


def test_not_authorized_user(client: TestClient, api_settings):
    # Только не авторизованный пользователь без авторизации
    response = client.get("/api/test/not_authorized_user")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "role": "visitor" }

    # Запрос токена на директора
    response_director_json = get_response_director_json(client, api_settings)

    # Только не авторизованный пользователь директором
    response = client.get("/api/test/not_authorized_user", headers=get_token_headers(response_director_json))
    assert response.status_code == 401
    assert response.json() == {"detail": "Already authorized username 'Paradox' role director" }

    # Запрос токена на пользователя
    response_user_json = get_response_user_json(client, api_settings)

    # Только не авторизованный пользователь пользователем
    response = client.get("/api/test/not_authorized_user", headers=get_token_headers(response_user_json))
    assert response.status_code == 401
    assert response.json() == {"detail": "Already authorized username 'User' role visitor" }