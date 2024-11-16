import uvicorn
from fastapi import FastAPI

from OAuth2.config import get_settings
from OAuth2.routers import auth, http_test

settings = get_settings()


# models.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(http_test.router, prefix='/api')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)