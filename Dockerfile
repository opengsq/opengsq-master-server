# Dockerfile
FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apk add --no-cache gcc musl-dev linux-headers \
    && pip install -r requirements.txt \
    && apk del musl-dev linux-headers

COPY . .
