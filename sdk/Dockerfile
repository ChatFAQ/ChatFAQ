FROM python:3.10-slim

# System req
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        make

# Copy only requirements to cache them in docker layer
WORKDIR /var/apps/sdk
COPY poetry.lock pyproject.toml README.md ./

# System deps:
ENV POETRY_VERSION=1.4.2
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python - \
    && poetry --version \
    && poetry config virtualenvs.in-project true \
    && poetry install --only main --no-interaction --no-ansi --no-root

RUN apt-get -y purge --auto-remove build-essential

COPY . .
RUN rm -rf .env

CMD [ "poetry", "run", "python", "-m", "examples.simple_example"]
