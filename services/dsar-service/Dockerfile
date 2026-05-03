FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml
COPY packages/common /app/packages/common
COPY services/dsar-service /app/services/dsar-service

WORKDIR /app/services/dsar-service

RUN uv sync --frozen

EXPOSE 8003

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}"]