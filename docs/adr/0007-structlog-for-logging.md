# ADR-007 — Use structlog for Structured JSON Logging

## Status

Accepted

## Context

Production services need searchable, filterable logs. Python's built-in logging outputs plain text which is impossible to filter by tenant or request in Railway's log viewer. We needed structured JSON logs with request context automatically bound to every log line.

## Decision

We chose structlog with stdlib LoggerFactory over plain logging or loguru.

## Consequences

- Every log line automatically includes tenant_id, user_id, org_role, request_id
- JSON output in production — searchable and filterable in Railway log viewer
- ConsoleRenderer in development — human-readable coloured output locally
- contextvars integration — async-safe context binding per request
- LoggingMiddleware generates request_id and adds X-Request-ID response header
- structlog requires one-time configuration at service startup via configure_logging()
