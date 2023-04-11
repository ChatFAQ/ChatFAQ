FROM modelw/base:2023.03

COPY --chown=user package.json package-lock.json ./

RUN modelw-docker run node --version && modelw-docker run npm --version && modelw-docker install

COPY --chown=user . .

ARG CHATFAQ_BACKEND_API
ENV CHATFAQ_BACKEND_API=$CHATFAQ_BACKEND_API
ARG CHATFAQ_BACKEND_WS
ENV CHATFAQ_BACKEND_WS=$CHATFAQ_BACKEND_WS

RUN modelw-docker build

CMD ["modelw-docker", "serve"]
