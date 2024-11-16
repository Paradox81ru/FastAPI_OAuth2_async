from datetime import datetime

from sqlalchemy import types


class MyDateTime(types.TypeDecorator):
    impl = types.DateTime
    
    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        return value