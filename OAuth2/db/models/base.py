from contextlib import contextmanager
from copy import copy
from typing import Container
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm import AttributeState
from sqlalchemy.inspection import inspect

from OAuth2.db.db_connection import engine


class Base(DeclarativeBase):
    def to_dict(self, *, exclude: list[str] = None):
        _exclude = copy(exclude) if exclude is not None else []
        _exclude.extend(('_sa_instance_state', ))
        mapper = inspect(self)
        # return mapper.dict
        fields = {}
        for field_name in mapper.dict:
            if field_name in _exclude:
                continue
            fields[field_name] = mapper.dict[field_name]
        return fields
    
    def __repr__(self) -> str:
        attrs = tuple(f"{field}={f'\'{value}\'' if isinstance(value, str) else value}" for field, value in self.to_dict().items())
        return f"{self.__class__.__name__}({', '.join(attrs)})"

class BaseManager:
    """ Менеджер (singleton) """
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, _db: AsyncSession):
        self._db = _db
