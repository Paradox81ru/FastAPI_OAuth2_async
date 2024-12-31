from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import get_settings

settings = get_settings()

engine = create_engine(settings.db_connect_str, echo=True)
db_session = Session(engine)

engine_async = create_async_engine(settings.db_connect_str, echo=settings.debug_mode)
db_session_async = AsyncSession(engine_async)
