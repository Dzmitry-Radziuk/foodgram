FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm cache clean --force && \
    npm install --legacy-peer-deps
COPY . ./
RUN npm run build


RUN mkdir -p result_build && cp -r build/* result_build/