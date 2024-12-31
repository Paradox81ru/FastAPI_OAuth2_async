import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware

from config import get_settings, get_logger
from fastapi_site.middlewares.authentication import JWTTokenAuthBackend
from fastapi_site.routers import http_test
from ui.routes import html

settings = get_settings()
logger = get_logger("main")

logger.debug("Start app")
app = FastAPI()

app.mount("/static", StaticFiles(directory="ui/static"), name="static")
app.include_router(http_test.router, prefix="/api")
app.include_router(html.router, prefix="")
app.add_middleware(AuthenticationMiddleware, 
                   backend=JWTTokenAuthBackend(settings.auth_server_host, settings.auth_server_port),
                   on_error=lambda conn, exc: JSONResponse({"detail": str(exc)}, status_code=401)
                   )

if __name__ == "__main__":
    uvicorn.run(app, host=settings.auth_test_host, port=settings.auth_test_port)
