FROM node:16.14.2-bullseye-slim

WORKDIR /client

COPY ./client/.npmrc .

COPY ./client/package*.json .

RUN npm install

COPY ./client/webpack.config.js .
