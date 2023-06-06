FROM modelw/base:2023.03

COPY --chown=user pyproject.toml poetry.lock ./

RUN modelw-docker install

COPY --chown=user . .

RUN modelw-docker build

CMD ["bash", "-c", "modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 chatfaq_retrieval_server.config.asgi:application"]
# CMD ["modelw-docker", "serve"]
