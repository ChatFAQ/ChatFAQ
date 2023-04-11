FROM python:3.10-slim

ENV POETRY_VERSION=1.3.1

# System deps:
RUN curl -sSL https://install.python-poetry.org | python -

# Copy only requirements to cache them in docker layer
WORKDIR /var/apps/sdk
COPY poetry.lock pyproject.toml README.md ./

# System req
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        make

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$ENV_TYPE" == production && echo "--no-dev") --no-interaction --no-ansi --no-root

RUN apt-get -y purge --auto-remove build-essential

COPY . .
RUN rm -rf .env

CMD [ "poetry", "run", "python", "-m", "examples.__init__"]
