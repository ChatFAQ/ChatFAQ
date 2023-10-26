FROM python:3.10-slim

# System req
RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential \
        make \
        libpq-dev \
        curl

RUN apt-get install -y curl
# Copy only requirements to cache them in docker layer
WORKDIR /var/apps/sdk
COPY poetry.lock pyproject.toml README.md ./

# System deps:
ENV POETRY_VERSION=1.5.1
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python - \
    && poetry --version \
    && poetry config installer.max-workers 10 \
    && poetry config virtualenvs.in-project true \
    && poetry install --only main --no-interaction --no-ansi --no-root

RUN apt-get -y purge --auto-remove build-essential make curl

COPY . .

CMD ["poetry", "run", "python", "-m", "examples.model_example"]
