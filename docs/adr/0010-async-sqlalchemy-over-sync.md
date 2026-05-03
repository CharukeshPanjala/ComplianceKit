# ADR-010 — Use Async SQLAlchemy over Sync

## Status

Accepted

## Context

FastAPI is built on async Python. Using synchronous SQLAlchemy with an async framework blocks the event loop during database operations, eliminating the concurrency benefits of async. We needed a database layer that works natively with Python's asyncio.

## Decision

We chose SQLAlchemy 2.0 with asyncpg driver and async session management.

## Consequences

- Non-blocking DB queries — event loop continues handling other requests during I/O
- asyncpg is the fastest PostgreSQL driver for Python
- async with session.begin() provides clean transaction management
- DATABASE_URL must use postgresql+asyncpg:// scheme — handled by fix_database_url() validator
- Alembic migrations run synchronously — env.py uses asyncio.run() to bridge async/sync
- Slightly more complex code — async generators and context managers vs simple function calls
