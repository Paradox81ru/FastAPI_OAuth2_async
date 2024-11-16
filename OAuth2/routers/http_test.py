
from typing import Annotated

from fastapi import APIRouter, Depends, Security

from OAuth2.dependencies import get_current_user, check_role, check_scope, is_auth, is_not_auth
from OAuth2.schemas import User, AnonymUser
from OAuth2.schemas import UserRoles

router = APIRouter(
    prefix='/test',
    tags=['test'])

@router.get("/get_user", response_model=User | AnonymUser)
async def get_user(current_user: Annotated[User | AnonymUser, Depends(get_current_user)]):
    return current_user


@router.get("/users/me", dependencies=[Security(check_scope, scopes=['me'])])
async def reader_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return  {"status": "ok", "username": current_user.username, "role": current_user.get_role() }


@router.get("/users/me/items", dependencies=[Security(check_scope, scopes=['me', 'items'])])
async def read_own_items(current_user: Annotated[User, Depends(get_current_user)]):
    return  {"status": "ok", "username": current_user.username, "role": current_user.get_role() }


@router.get("/status")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok", "username": current_user.username, "role": current_user.get_role()}


@router.get("/only_admin", dependencies=[Depends(check_role([UserRoles.admin]))])
async def read_only_admin(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok", "role": current_user.get_role()}


@router.get("/only_director", dependencies=[Depends(check_role([UserRoles.director]))])
async def read_only_director(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok", "role": current_user.get_role()}


@router.get("/authorized_user", dependencies=[Depends(is_auth)])
async def read_authorized_user(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok", "username": current_user.username,  "role": current_user.get_role()}


@router.get("/not_authorized_user", dependencies=[Depends(is_not_auth)])
async def read_authorized_user(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok", "role": current_user.get_role()}