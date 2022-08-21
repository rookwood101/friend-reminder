ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}

RUN apt-get update && apt-get install -y supervisor cron

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /app
WORKDIR /app

COPY jobs.cron ./
RUN crontab jobs.cron

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true --local \
 && poetry install --no-dev

COPY . .

RUN poetry run python manage.py collectstatic --noinput


CMD ["/usr/bin/supervisord", "-n", "-c", "supervisord.conf"]

EXPOSE 8080
