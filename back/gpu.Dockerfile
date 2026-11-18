FROM modelw/base:2026.10

COPY --chown=user model-w.toml pyproject.toml poetry.lock README.md ./

# For PDF parsing
# RUN apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra


RUN modelw-docker install \
    && modelw-docker run poetry run playwright install firefox

# Install GPU pytorch
ARG TORCH_GPU_URL=https://download.pytorch.org/whl/cu128/torch-2.10.0%2Bcu128-cp314-cp314-manylinux_2_28_x86_64.whl
RUN modelw-docker run poetry add ${TORCH_GPU_URL}

COPY --chown=user . .

RUN modelw-docker build

CMD ["bash", "-c", "modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application"]
