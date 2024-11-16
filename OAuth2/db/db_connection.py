# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from OAuth2.config import get_settings

settings = get_settings()

# engine = create_engine(settings.db_connect_str, echo=True)
engine = create_async_engine(settings.db_connect_str, echo=True)
# db_session = Session(engine)
db_session = AsyncSession(engine)
