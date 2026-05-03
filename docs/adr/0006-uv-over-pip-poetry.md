# ADR-006 — Use uv over pip/poetry

## Status

Accepted

## Context

We needed a Python package manager that supports workspaces (multiple packages in one repo), fast dependency resolution, and a reliable lockfile. Options were pip+venv, Poetry, and uv.

## Decision

We chose uv over pip and Poetry.

## Consequences

- 10-100x faster than pip for dependency resolution and installation
- Native workspace support — all 4 services and common share one lockfile
- uv sync --frozen in Dockerfiles ensures reproducible builds
- Drop-in replacement for pip — standard pyproject.toml format
- Relatively new tool — less community documentation than Poetry
- Lockfile (uv.lock) committed to repo ensures identical environments everywhere
