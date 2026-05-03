# ADR-005 — Use a Monorepo over Separate Repositories

## Status

Accepted

## Context

ComplianceKit has 4 backend services, 1 frontend, and shared Python utilities. We could organise these as separate repositories or a single monorepo. For an early-stage product with one developer, coordination overhead between repos is a significant cost.

## Decision

We chose a shared monorepo with uv workspaces for Python and pnpm workspaces for Node.

## Consequences

- Shared packages/common used by all Python services without publishing to PyPI
- Single CI pipeline — one GitHub Actions workflow covers all services
- Atomic commits — a change to common + a service change ships together
- Watch paths in Railway railway.toml ensure only affected services redeploy
- As team grows, monorepo tooling (Nx, Turborepo) may be needed
- Larger clone size — developers download all services even if they only work on one
