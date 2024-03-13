# Stage 1: Use python:3.12 to install dependencies
FROM python:3.12 as builder

WORKDIR /app

RUN python -m venv venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Use python:3.12-alpine and copy installed dependencies from builder stage
FROM python:3.12-alpine

WORKDIR /app

ENV PATH="/venv/bin:$PATH"

COPY --from=builder venv venv
COPY . .
