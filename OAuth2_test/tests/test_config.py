
def test_oauth2_config(oauth2_settings):
    """
    Проверяет загрузку конфигурации модуля oauth2.
    :param oauth2_settings: Настройки oauth2 сервера.
    :raises AssertionError:
    """
    assert oauth2_settings.init_admin_password != ''
    assert oauth2_settings.init_director_name != '' and oauth2_settings.init_director_name != 'Boss'


def test_oauth2_test_config(api_settings):
    """
    Проверяет загрузку конфигурации текущего модуля oauth2_test.
    :param api_settings: Настройки приложения.
    :raises AssertionError:
    """
    assert api_settings.auth_test_port == 8000
    assert api_settings.auth_server_port == 8001