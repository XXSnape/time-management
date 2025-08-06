FROM python:3.12-slim

WORKDIR /bot

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml .env ./

RUN poetry install --without lint

COPY . .
