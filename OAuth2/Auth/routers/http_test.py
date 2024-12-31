
from typing import Annotated

from fastapi import APIRouter, Depends, Security

from Auth.dependencies import get_current_user_and_scope, check_role, check_scope, is_auth, is_not_auth
from Auth.schemas import User
from Auth.schemas import UserRoles

router = APIRouter(
    prefix='/test',
    tags=['test'])


@router.get("/scope/me", dependencies=[Security(check_scope, scopes=['me'])])
async def reader_users_me(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, если при авторизации был указан scope 'me'. """
    user, scopes = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role(), "scopes": scopes}


@router.get("/scope/me_items", dependencies=[Security(check_scope, scopes=['me', 'items'])])
async def reader_users_me(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если при авторизации были указаны scope 'me' и 'items'. """
    user, scopes = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role(), "scopes": scopes}


@router.get("/only_admin", dependencies=[Depends(check_role([UserRoles.admin]))])
async def get_only_admin(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если он имеет роль администратора. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_director", dependencies=[Depends(check_role([UserRoles.director]))])
async def get_only_director(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если он имеет роль директора. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_admin_or_director", dependencies=[Depends(check_role([UserRoles.admin, UserRoles.director]))])
async def get_only_admin_or_director(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если он имеет роль администратора или директора. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_user", dependencies=[Depends(check_role([UserRoles.visitor]))])
async def get_only_user(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если он имеет роль посетителя. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_authorized_user", dependencies=[Depends(is_auth)])
async def get_authorized_user(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает текущего пользователя, только если он авторизован. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username,  "role": user.get_role()}


@router.get("/only_anonym_user", dependencies=[Depends(is_not_auth)])
async def get_not_authorized_user(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Возвращает анонимного пользователя, только если на сайте нет авторизации. """
    user, _ = user_and_scope
    return {"status": "ok", "username": user.username,  "role": user.get_role()}


@router.get("/status")
async def read_system_status(user_and_scope: Annotated[tuple[User, list], Depends(get_current_user_and_scope)]):
    """ Просто проверка статуса текущего пользователя. """
    current_user, scope = user_and_scope
    return {"status": "ok", "username": current_user.username, "role": current_user.get_role()}
