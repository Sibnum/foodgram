FROM node:21-alpine AS build
WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . ./

RUN npm run build

RUN npm install -g http-server

CMD ["http-server", "-p", "8000", "/app/build"]