# ADR-004 — Use Railway for MVP Hosting

## Status

Accepted

## Context

We needed a hosting platform for the MVP. Options were AWS (ECS/RDS), Heroku, Render, and Railway. For an MVP, developer experience and time-to-deploy matter more than raw infrastructure control.

## Decision

We chose Railway over AWS, Heroku, and Render.

## Consequences

- Zero infrastructure config — no VPCs, security groups, or load balancers to manage
- Managed Postgres and Redis with volumes and backups built-in
- GitHub source deployment — push to main triggers automatic deploy
- Private networking between services via .railway.internal — no egress costs
- Config as code via railway.toml — deployment config tracked in git
- Less control than AWS — not suitable for enterprise compliance requirements long-term
- Free tier limited to 5 services — Hobby plan needed for full stack
