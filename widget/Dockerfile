# Dockerfile
FROM node:19-alpine3.16

# create destination directory
WORKDIR /var/apps/widget

# update and install dependency
RUN apk update && apk upgrade

# copy the app, note .dockerignore
COPY . .
RUN npm install
RUN npm run build

EXPOSE 3000

CMD [ "node", ".output/server/index.mjs" ]
