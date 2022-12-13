FROM python:3.8-slim

ENV VIRTUAL_ENV /opt/venv
ENV PYTHONHASHSEED=0

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .

RUN apt-get -y update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        locales \
    && apt-get install -y procps vim git tini \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && locale-gen \
    && apt-get -y purge --auto-remove \
        build-essential \
    && pip uninstall -y wheel \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && rm -rf requirements.txt

WORKDIR /home/app

COPY . .

EXPOSE 8000

COPY docker-entrypoint.sh /docker-entrypoint.sh
CMD [ "/bin/bash", "/docker-entrypoint.sh"]
