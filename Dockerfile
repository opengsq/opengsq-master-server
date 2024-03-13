# Stage 1: Use python:3.12 to install dependencies
FROM python:3.12 as builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install psutil

# Stage 2: Use python:3.12-alpine and copy installed dependencies from builder stage
FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
