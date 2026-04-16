FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml
COPY packages/common /app/packages/common
COPY services/document-generator /app/services/document-generator

WORKDIR /app/services/document-generator

RUN uv sync --frozen

EXPOSE 8002

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]