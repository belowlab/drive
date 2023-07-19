# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster
WORKDIR /app

COPY requirements.txt /app/requirements.txt
# make sure we have the newest version of pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./drive /app/drive/