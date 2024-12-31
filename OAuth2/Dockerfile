FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

# Секретный ключ для шифрования и дешифрования токена.
# ENV SECRET_KEY="11dcfbb19316b6104037b2ec8d6d0179b89f55a93da4594e4971d96df5feae21"
# Время жизни токена доступа.
# ENV ACCESS_TOKEN_EXPIRE_MINUTES=10
# Время жизни токена обновления.
# ENV REFRESH_TOKEN_EXPIRE_MINUTES=60
# Соединение с базой данных.
# ENV DB_CONNECT_STR="sqlite:///db.sqlite3"

# Данные для инициализации пользователей в бае данных.
# ENV INIT_ADMIN_EMAIL="admin@yandex.ru"
# ENV INIT_SYSTEM_EMAIL="system@gmail.com"
# ENV INIT_DIRECTOR_LOGIN="Boroda"
# ENV INIT_DIRECTOR_NAME="Фёдор"
# ENV INIT_DIRECTOR_LASTNAME="Петрович"
# ENV INIT_DIRECTOR_EMAIL="boroda@mail.ru"
# ENV INIT_USER_LOGIN="Pups"
# ENV INIT_USER_NAME="Малой"
# ENV INIT_USER_LASTNAME=""
# ENV INIT_USER_EMAIL="pups@hotmail.com"


# Пароли для пользователей при инициализации базы данных.
# ENV INIT_ADMIN_PASSWORD="Pups_555"
# ENV INIT_SYSTEM_PASSWORD="Pups_555"
# ENV INIT_DIRECTOR_PASSWORD="Pups_555"
# ENV INIT_USER_PASSWORD="Pups_555"

# ENV DEBUG_MODE="True"

WORKDIR /app

COPY .  /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN alembic upgrade head

EXPOSE 8001

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
