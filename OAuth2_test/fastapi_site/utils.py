def get_authorization_scheme_param(authorization_header_value: str | None) -> tuple[str, str]:
    """ Возвращает схему и параметр авторизации. """
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param