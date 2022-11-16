FROM python:3.10.4-slim-bullseye

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /server

COPY ./server/requirements ./requirements

RUN pip install -r requirements/dev.txt
