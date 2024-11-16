from OAuth2.config import get_settings
import os

def test_settings():
    settings = get_settings()
    assert 'IS_TEST' in os.environ and os.environ['IS_TEST'] == 'True'
    assert settings.access_token_expire_minutes == 1
    assert settings.refresh_token_expire_minutes == 5
    assert settings.db_connect_str == 'sqlite:///db-test.sqlite3'
