ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /app
WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true --local
RUN poetry install --no-dev

COPY . .

RUN poetry run python manage.py collectstatic --noinput


EXPOSE 8080

# replace APP_NAME with module name
CMD ["poetry", "run", "gunicorn", "--bind", ":8080", "--workers", "2", "friend_reminder.wsgi"]
