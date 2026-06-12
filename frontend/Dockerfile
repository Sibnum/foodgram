FROM node:21-alpine as build
WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . ./

RUN npm run build
