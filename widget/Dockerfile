FROM modelw/base:2026.10

COPY --chown=user .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN modelw-docker install

COPY --chown=user . .

ARG NUXT_PUBLIC_CHATFAQ_API
ENV NUXT_PUBLIC_CHATFAQ_API=$NUXT_PUBLIC_CHATFAQ_API
ARG NUXT_PUBLIC_CHATFAQ_WS
ENV NUXT_PUBLIC_CHATFAQ_WS=$NUXT_PUBLIC_CHATFAQ_WS
ARG NUXT_PUBLIC_BASE_URL
ENV NUXT_PUBLIC_BASE_URL=$NUXT_PUBLIC_BASE_URL

RUN modelw-docker build

CMD ["modelw-docker", "serve"]
