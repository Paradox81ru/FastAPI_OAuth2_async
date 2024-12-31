
from fastapi import HTTPException, status


class AuthenticateException(HTTPException):
    """ Собственное исключение ошибки авторизации"""
    def __init__(self, detail: str, authenticate_value: str | None = "Bearer"):
        """
        Конструктор класса.
        :param detail: Подробная информация об ошибке.
        :param authenticate_value: Параметр авторизации.
        """
        headers={"WWW-Authenticate": authenticate_value}
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)