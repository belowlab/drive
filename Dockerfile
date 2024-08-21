# FROM python:3.11-slim-bullseye as build-container
FROM debian:12.6-slim as build-container

# changing the working directory to be app
WORKDIR /app/

# We need to install curl
RUN apt-get update \
    && apt-get install -y curl python3.11 python3.11-venv\
    && rm -rf /var/lib/apt/lists/* 

RUN python3.11 -m venv venv

# RUN PYTHON=$(command -v python3.11)
# RUN ln -s ${PYTHON} /usr/bin/python

# Copy the requirements file into the container
COPY ./drive ./drive
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
COPY ./README.md /app/README.md

# Now we can configure our environment to install things with poetry
ARG BUILD_ENV

ENV BUILD_ENV=${BUILD_ENV} \
PIP_NO_CACHE_DIR=1 \
POETRY_VERSION=1.8.3 \
POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_CREATE=false \
POETRY_CACHE_DIR='/var/cache/pypoetry' \
POETRY_HOME='/usr/local'

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3.11 - 
RUN PATH="/root/.local/bin:$PATH"
RUN poetry self add poetry-plugin-bundle


# Use poetry to install dependencies into the virtualenv
RUN poetry bundle venv --python venv/bin/python /app/venv/ 

# Now we can create the runtime container and just copy the virtualenv to this container
FROM debian:12.6-slim as runtime-container

RUN apt-get update \
    && apt-get install -y python3.11 \
    && rm -rf /var/lib/apt/lists/* 

LABEL maintainer="belowlab"
LABEL version="2.7.4"

# Copy and activate the virtualenv
COPY --from=build-container /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
