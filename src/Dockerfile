FROM python:3.12-slim AS base
LABEL authors="treysenzobell"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    curl \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME="$POETRY_HOME" python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN poetry self add poetry-plugin-shell

WORKDIR /app
COPY ../pyproject.toml ../README.md ./src ./static ./
RUN poetry lock && poetry install

RUN poetry run python manage.py makemigrations
RUN poetry run python manage.py collectstatic --no-input

ENTRYPOINT ["sh", "-c", "poetry run python manage.py migrate && poetry run gunicorn runnersutah.wsgi:application --bind 0.0.0.0:8000"]
#CMD ["sleep", "infinity"]