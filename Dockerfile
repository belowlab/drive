FROM python:3.11-slim-bullseye as build-container

# changing the working directory to be app
WORKDIR /app/

# We need to install curl
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* 

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
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry self add poetry-plugin-bundle

# Use poetry to install dependencies into the virtualenv
RUN poetry bundle venv /opt/venv/

# Now we can create the runtime container and just copy the virtualenv to this container
FROM python:3.11-slim-bullseye as runtime-container


LABEL maintainer="belowlab"
LABEL version="2.7.1"

# Copy and activate the virtualenv
COPY --from=build-container /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
