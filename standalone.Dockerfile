# We'll use latest, since this is used to run tests only.
FROM docker:latest

ENV PYTHONDONTWRITEBYTECODE 1
# Brings output to the terminal:
ENV PYTHONUNBUFFERED 1

RUN apk update

COPY . .
COPY ./docker-compose.standalone.yml ./docker-compose.override.yml
