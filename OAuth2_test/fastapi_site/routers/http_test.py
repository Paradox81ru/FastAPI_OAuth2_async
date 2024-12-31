from fastapi import APIRouter, Depends, Request, Security

from fastapi_site.dependencies import check_scope, check_role, is_auth, is_anonym_user
from fastapi_site.schemas import AnonymUser, User, UserRoles

router = APIRouter(
    prefix="/test",
    tags=['test']
)

# @router.get("/get_user")
# async def get_user(bearer_authorization: Annotated[User | AnonymUser, Depends(validate_jwt_token)]):
#     if bearer_authorization == None:
#         return AnonymUser()
#     api_url = "http://127.0.0.1:8001/api/test/get_user"
#     async with httpx.AsyncClient() as client:
#         response = await client.get(api_url, headers={"Authorization": bearer_authorization})
#         user = response.json()
#         return User(**user)
#     return AnonymUser()


@router.get("/get_user", response_model=tuple[User, list] | tuple [AnonymUser, list])
async def get_user(request: Request):
    """ Возвращает текущего пользователя и его scope. """
    user = request.user
    scopes = request.auth.scopes
    return user, scopes


@router.get("/scope/me", dependencies=[Security(check_scope, scopes=['me'])])
async def get_user_scope_me(request: Request):
    """ Возвращает текущего пользователя, если при авторизации был указан scope 'me'. """
    user = request.user
    scopes = request.auth.scopes
    return {"status": "ok", "username": user.username, "role": user.get_role(), "scopes": scopes}


@router.get("/scope/me_items", dependencies=[Security(check_scope, scopes=['me', 'items'])])
async def get_user_scopes_me_and_items(request: Request):
    """ Возвращает текущего пользователя, только если при авторизации были указаны scope 'me' и 'items'. """
    user = request.user
    scopes = request.auth.scopes
    return  {"status": "ok", "username": user.username, "role": user.get_role(), "scopes": scopes}


@router.get("/only_admin", dependencies=[Depends(check_role([UserRoles.admin]))])
async def get_only_admin(request: Request):
    """ Возвращает текущего пользователя, только если он имеет роль администратора. """
    user = request.user
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_director", dependencies=[Depends(check_role([UserRoles.director]))])
async def get_only_director(request: Request):
    """ Возвращает текущего пользователя, только если он имеет роль директора. """
    user = request.user
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_admin_or_director", dependencies=[Depends(check_role([UserRoles.admin, UserRoles.director]))])
async def get_only_admin_or_director(request: Request):
    """ Возвращает текущего пользователя, только если он имеет роль администратора или директора. """
    user = request.user
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_user", dependencies=[Depends(check_role([UserRoles.visitor]))])
async def get_only_user(request: Request):
    """ Возвращает текущего пользователя, только если он имеет роль посетителя. """
    user = request.user
    return {"status": "ok", "username": user.username, "role": user.get_role()}


@router.get("/only_authorized_user", dependencies=[Depends(is_auth)])
async def get_authorized_user(request: Request):
    """ Возвращает текущего пользователя, только если он авторизован. """
    user = request.user
    return {"status": "ok", "username": user.username,  "role": user.get_role()}


@router.get("/only_anonym_user", dependencies=[Depends(is_anonym_user)])
async def get_not_authorized_user(request: Request):
    """ Возвращает анонимного пользователя, только если на сайте нет авторизации. """
    user = request.user
    return {"status": "ok", "username": user.username,  "role": user.get_role()}