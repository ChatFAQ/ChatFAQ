FROM python:3.10.13-slim

ARG MODEL_W_PIP_EXTRA=""

RUN python -m venv /opt/model-w  \
    && /opt/model-w/bin/python -m pip install --no-cache-dir $MODEL_W_PIP_EXTRA 'modelw-docker==2023.4.0b4' \
    && ln -s /opt/model-w/bin/modelw-docker /usr/local/bin/modelw-docker

RUN mkdir /code \
    && useradd -d /code -s /bin/bash user \
    && chown -R user:user /code

COPY --chown=user model-w.toml pyproject.toml poetry.lock README.md ./

# For PDF parsing
# RUN apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update  \
    && apt-get install -y curl ca-certificates gnupg apt-transport-https lsb-release \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor --output /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg \
    && curl https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor --output /etc/apt/trusted.gpg.d/nodesource.gpg

COPY ./sources.list /etc/apt/sources.list

RUN apt-get update  \
    && apt-get install -y \
        # Common project dependencies
        libpcre3 \
        libpcre3-dev \
        mime-support \
        postgresql-client \
        libpq-dev \
        gdal-bin \
        gdal-data \
        # Things required to build Python
        build-essential \
        gcc \
        g++ \
        make \
        libssl-dev  \
        zlib1g-dev \
        libbz2-dev  \
        libreadline-dev  \
        libsqlite3-dev  \
        llvm \
        libncursesw5-dev \
        xz-utils  \
        tk-dev  \
        libxml2-dev  \
        libxmlsec1-dev  \
        libffi-dev  \
        liblzma-dev \
        # Things required to build Pillow
        libtiff5-dev  \
        libjpeg-dev  \
        libopenjp2-7-dev  \
        zlib1g-dev \
        libfreetype6-dev  \
        liblcms2-dev  \
        libwebp-dev  \
        tcl8.6-dev  \
        tk8.6-dev  \
        libharfbuzz-dev  \
        libfribidi-dev  \
        libxcb1-dev \
        # NodeJS
        nodejs \
        # Things required to use Weasyprint
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        # Stuff for unstructured pdf parsing
        poppler-utils \
        # Stuff to allow configuration afterwards
        sudo \
    && apt-get upgrade -y \
    && rm -fr \
        /var/log/alternatives.log \
        /var/log/apt/history.log \
        /var/log/apt/term.log \
        /var/log/bootstrap.log \
        /var/log/dpkg.log \
        /var/cache/man \
        /var/cache/ldconfig/aux-cache \
        /etc/machine-id \
        /var/cache/apt

RUN echo "user ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/model-w \
    && chmod 0440 /etc/sudoers.d/model-w

RUN curl -sSL https://install.python-poetry.org | env POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

RUN modelw-docker install \
    && modelw-docker run poetry run playwright install-deps \
    && modelw-docker run poetry run playwright install firefox \
    && poetry run pip uninstall -y effdet

COPY --chown=user . .

RUN modelw-docker build


# For installing chat-rag full for back based images with all the AI functionality and libraries.
ARG INSTALL_CHAT_RAG
ENV INSTALL_CHAT_RAG=$INSTALL_CHAT_RAG

RUN if [ "$INSTALL_CHAT_RAG" = "true" ]; then echo "Installing nvidia-cudnn-cu12..."; poetry add nvidia-cudnn-cu12==8.9.2.26; fi
RUN if [ "$INSTALL_CHAT_RAG" = "true" ]; then echo "Installing chat-rag..."; poetry add chat-rag[full]==0.1.81; fi
RUN if [ "$INSTALL_CHAT_RAG" = "true" ]; then echo "Installing ninja-build..."; apt-get install ninja-build; fi

ENV RAY_task_events_max_num_task_in_gcs=100

CMD ./starter_script.sh
