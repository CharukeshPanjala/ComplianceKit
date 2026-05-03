# ADR-001 — Use FastAPI over Django

## Status

Accepted

## Context

ComplianceKit needs a Python backend framework for building REST APIs. The two main options were Django (with Django REST Framework) and FastAPI. We needed async support for handling concurrent requests efficiently, automatic OpenAPI documentation, and strong type hints throughout the codebase.

## Decision

We chose FastAPI over Django/DRF.

## Consequences

- Native async/await support — handles concurrent DB calls and external API calls efficiently
- Automatic OpenAPI docs at /docs — no extra setup needed
- Pydantic models give us runtime validation and type safety
- Lighter than Django — no ORM, no admin, no templating engine we don't need
- We manage our own DB layer (SQLAlchemy) — more control but more setup
- Smaller ecosystem than Django — fewer built-in batteries
