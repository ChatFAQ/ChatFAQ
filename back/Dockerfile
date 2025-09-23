FROM modelw/base:2025.07

COPY --chown=user pyproject.toml poetry.lock ./

RUN modelw-docker install

COPY --chown=user . .

RUN modelw-docker build

CMD ["modelw-docker", "serve"]