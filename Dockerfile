FROM debian:bookworm-slim AS build-container

# changing the working directory to be app
WORKDIR /app/

# We need to install curl
RUN apt-get update \
    && apt-get install -y curl python3.11 python3-venv git\
    && rm -rf /var/lib/apt/lists/* 

# RUN python3.11 -m venv venv

# RUN PYTHON=$(command -v python3.11)
# RUN ln -s ${PYTHON} /usr/bin/python

# Copy the requirements file into the container
COPY ./src /app/src
COPY ./tests /app/tests
COPY ./pyproject.toml /app/pyproject.toml
COPY ./pdm.lock /app/pdm.lock
COPY LICENSE /app/LICENSE
COPY ./README.md /app/README.md

RUN curl -sSL https://pdm-project.org/install-pdm.py | python3.11 -

ENV PATH=/root/.local/bin:$PATH
# disable update check
ENV PDM_CHECK_UPDATE=false

RUN pdm install --check --prod --no-editable
RUN pdm run pytest ./tests/test_integration.py -v

# Now we can create the runtime container and just copy the virtualenv to this container
FROM debian:bookworm-slim as runtime-container

RUN apt-get update \
    && apt-get install -y python3.11 python3-venv \
    && rm -rf /var/lib/apt/lists/* 

LABEL maintainer="belowlab"
LABEL version="2.7.15b1"

# Copy and activate the virtualenv
COPY --from=build-container /app/.venv/ /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
