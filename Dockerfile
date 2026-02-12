FROM python:3.12.5-slim

ENV POETRY_VERSION=1.8.3
RUN pip install "poetry==$POETRY_VERSION"

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /tz-auth

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-ansi
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY . .

COPY wait_for_pg.sh /usr/local/bin/wait_for_pg.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/wait_for_pg.sh /usr/local/bin/entrypoint.sh

EXPOSE 80

ENTRYPOINT ["entrypoint.sh"]
