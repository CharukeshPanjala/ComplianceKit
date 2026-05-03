# ADR-009 — Use GitHub Source Deployment over Pre-built GHCR Images

## Status

Accepted

## Context

Railway can deploy from two sources: pre-built Docker images from a registry (GHCR) or directly from GitHub source code using our Dockerfiles. We initially used GHCR images built in GitHub Actions but switched during COM-23 when pre-deploy commands and railway.toml config-as-code did not work with image-based deployments.

## Decision

We switched from GHCR Docker image deployment to GitHub source deployment.

## Consequences

- railway.toml config-as-code works — pre-deploy command, healthcheck, restart policy all tracked in git
- Pre-deploy Alembic migrations run reliably before every deployment
- Railway builds from our Dockerfiles directly — no separate build workflow needed
- Disabled COM-22 GitHub Actions deploy workflow — Railway handles builds
- Build time counts against Railway's build quota — GitHub Actions was free
- Slightly slower deploys — Railway builds on each push vs pulling pre-built image
