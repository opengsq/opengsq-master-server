# Dockerfile
FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apk add --no-cache python3-dev \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
