FROM node:18-alpine as build

RUN adduser -D nuxtuser

USER nuxtuser

# set work dir as app
WORKDIR /app

COPY package.json package-lock.json ./

COPY . .

RUN npm ci --prefer-local \
    && npx nuxt build

FROM node:18-alpine as runtime
RUN apk update && apk upgrade && apk --no-cache add dumb-init

FROM runtime

RUN adduser -D nuxtuser
USER nuxtuser
WORKDIR /app

# copy the output directory to the /app directory from
# build stage with proper permissions for user nuxt user
COPY --chown=nuxtuser:nuxtuser --from=build /app/.output ./

# set app host and port . In nuxt 3 this is based on nitor and you can read
#more on this https://nitro.unjs.io/deploy/node#environment-variables
ENV HOST=0.0.0.0 \
    PORT=${PORT:-3000} \
    NODE_ENV=production

# start the app with dumb init to spawn the Node.js runtime process
# with signal support
CMD ["dumb-init", "node", "/app/server/index.mjs"]
