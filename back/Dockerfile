FROM modelw/base:2023.04

COPY --chown=user README.md pyproject.toml poetry.lock README.md ./

RUN modelw-docker install

COPY --chown=user . .

RUN modelw-docker build

CMD ["bash", "-c", "modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application"]
