FROM modelw/base:2023.03

COPY --chown=user package.json package-lock.json ./

RUN modelw-docker install

COPY --chown=user . .

ARG NUXT_API_URL
ENV NUXT_API_URL=$NUXT_API_URL
ARG NUXT_PROXY_OPTIONS_TARGET
ENV NUXT_PROXY_OPTIONS_TARGET=$NUXT_PROXY_OPTIONS_TARGET


RUN modelw-docker build

CMD ["modelw-docker", "serve"]
