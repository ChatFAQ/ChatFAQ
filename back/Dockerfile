FROM modelw/base:2023.04

COPY --chown=user pyproject.toml poetry.lock README.md ./

# For PDF parsing
# RUN apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra

RUN modelw-docker install \
    && modelw-docker run poetry run playwright install firefox

COPY --chown=user . .

RUN modelw-docker build

CMD ["bash", "-c", "modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application"]
