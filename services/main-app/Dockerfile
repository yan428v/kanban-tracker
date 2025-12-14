FROM python:3.13

WORKDIR /code

ENV PYTHONPATH=src

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock README.md ./

RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-root --no-interaction --no-ansi

COPY ./src /code/src
COPY ./settings.toml /code/settings.toml