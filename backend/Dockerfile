FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml .env create_certs.py ./

RUN poetry install --without lint,test

COPY . .

CMD python create_certs.py && alembic upgrade head && python main.py