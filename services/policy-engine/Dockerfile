FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml
COPY packages/common /app/packages/common
COPY services/policy-engine /app/services/policy-engine

WORKDIR /app/services/policy-engine

RUN uv sync --frozen

EXPOSE 8001

# MODE=api (default) or MODE=worker
CMD ["sh", "-c", "if [ \"$MODE\" = 'worker' ]; then uv run arq app.workers.assessment.WorkerSettings; else uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}; fi"]