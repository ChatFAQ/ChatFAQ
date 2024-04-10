FROM modelw/base:2023.04

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV GPG_KEY A035C8C19219BA821ECEA86B64E628F8D684696D
ENV PYTHON_MAJOR_VERSION 3.10.13

COPY --chown=root install_python.sh /tmp/install_python.sh
USER root
RUN chmod a+x /tmp/install_python.sh
RUN /tmp/install_python.sh
RUN rm -fr /tmp/install_python.sh

ARG MODEL_W_PIP_EXTRA=""

# RUN python -m venv /opt/model-w \
#     && /opt/model-w/bin/python -m pip install --no-cache-dir $MODEL_W_PIP_EXTRA 'modelw-docker==2023.04' \
#     && ln -s /opt/model-w/bin/modelw-docker /usr/local/bin/modelw-docker

COPY --chown=user model-w.toml pyproject.toml poetry.lock README.md ./

# For PDF parsing
# RUN apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra

RUN modelw-docker install \
    && modelw-docker run poetry run playwright install firefox

RUN poetry run pip uninstall -y effdet

COPY --chown=user . .

RUN modelw-docker build

CMD ./entrypoint.sh
