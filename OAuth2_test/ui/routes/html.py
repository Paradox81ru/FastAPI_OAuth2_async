from fastapi import APIRouter, Request

from config import templates

router = APIRouter(
    prefix="",
    tags=["html"]
)

@router.get("/index")
async def main(request: Request):
    """ Главная HTML страница. """
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
