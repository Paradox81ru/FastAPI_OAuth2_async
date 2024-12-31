FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

# Хост микросервиса авторизации.
# ENV AUTH_SERVER_HOST="oauth2"
# Порт микросервиса авторизации.
# ENV AUTH_SERVER_PORT=8001

# ENV DEBUG_MODE="True"

WORKDIR /app

COPY .  /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
