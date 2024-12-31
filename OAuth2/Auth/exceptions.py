
from fastapi import HTTPException, status


class AuthenticateException(HTTPException):
    def __init__(self, detail: str, authenticate_value: str | None = "Bearer"):
        headers = {"WWW-Authenticate": authenticate_value}
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)
