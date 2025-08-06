FROM python:3.12-slim

WORKDIR /app

COPY poetry.lock pyproject.toml .env create_certs.py ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --without lint,test --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY . .

CMD python create_certs.py && alembic upgrade head && python main.py