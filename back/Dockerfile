FROM python:3.10-slim

# development, production
ARG ENV_TYPE

ENV BUILD_MODE=yes

ENV POETRY_VERSION=1.3.1

ENV DOCKER_CONTAINER Yes

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /var/apps/back
COPY poetry.lock pyproject.toml ./

# System req
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gdal-bin \
        make

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_TYPE" == production && echo "--no-dev") --no-interaction --no-ansi --no-root

RUN apt-get -y purge --auto-remove build-essential

COPY . .
RUN rm -rf .env

EXPOSE 8000

COPY docker-entrypoint.sh /docker-entrypoint.sh
CMD [ "/bin/bash", "/docker-entrypoint.sh"]
