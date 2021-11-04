FROM python:3.10-slim-buster

WORKDIR /app

COPY . .

RUN python -m pip install poetry
RUN poetry install

CMD "poetry run celery -A tasks worker --loglevel=INFO"
