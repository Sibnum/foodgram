FROM node:21-alpine as build
WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . ./

RUN npm run build
