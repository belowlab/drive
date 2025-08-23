FROM debian:bookworm-slim AS build-container
# FROM python:3.11-slim-bookworm AS build-container


# ENV PDM_CHECK_UPDATE=false
# RUN pip install pdm==2.24.0
# changing the working directory to be app
WORKDIR /app/

# We need to install curl
RUN apt-get update \
  && apt-get install -y curl python3.11 python3.11-venv git\
  && rm -rf /var/lib/apt/lists/* 


# Copy the requirements file into the container
COPY ./src /app/src
COPY ./tests /app/tests
COPY ./pyproject.toml /app/pyproject.toml
COPY ./pdm.lock /app/pdm.lock
COPY LICENSE /app/LICENSE
COPY ./README.md /app/README.md

RUN curl -sSL https://pdm-project.org/install-pdm.py | python3.11 - 

ENV PATH=/root/.local/bin:$PATH
# # # # disable update check
ENV PDM_CHECK_UPDATE=false
#
# # Now we can create the runtime container and just copy the virtualenv to this container
RUN pdm install --check --prod --no-editable -v 
RUN pdm run drive utilities test
# RUN pdm run pytest -v tests/test_integration.py

# # Now we can create the runtime container and just copy the virtualenv to this container
FROM debian:bookworm-slim AS runtime-container

RUN apt-get update \
  && apt-get install -y python3.11 python3-venv \
  && rm -rf /var/lib/apt/lists/* 

LABEL maintainer="belowlab"
LABEL version="3.0.2"

# # Copy and activate the virtualenv
COPY --from=build-container /app/.venv/ /app/.venv
COPY --from=build-container /app/LICENSE /app/LICENSE
COPY --from=build-container /app/tests /app/tests

ENV PATH="/app/.venv/bin:$PATH"
