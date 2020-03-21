FROM python:3.6-alpine

WORKDIR "/application"

COPY . /application
ENV PYTHONPATH "${PYTHONPATH}:/application"

RUN apk add -U --no-cache gcc build-base linux-headers ca-certificates python3-dev libffi-dev libressl-dev libxslt-dev \
    && pip install python-telegram-bot --upgrade \
    && pip install requests \
    && pip install Flask \
    && pip install apscheduler


ENTRYPOINT python3 ./src/Application.py
