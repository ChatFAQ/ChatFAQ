FROM modelw/base:2023.03

COPY --chown=user package.json package-lock.json ./

RUN modelw-docker install

COPY --chown=user . .

ARG CHATFAQ_API
ENV CHATFAQ_API=$CHATFAQ_API
ARG CHATFAQ_WS
ENV CHATFAQ_WS=$CHATFAQ_WS
ARG BASE_URL
ENV BASE_URL=$BASE_URL
ARG NUXT_PUBLIC_BASE_URL
ENV NUXT_PUBLIC_BASE_URL=$NUXT_PUBLIC_BASE_URL

RUN modelw-docker build

CMD ["modelw-docker", "serve"]
