# ADR-003 — Use PostgreSQL Row Level Security for Multi-tenancy

## Status

Accepted

## Context

ComplianceKit serves multiple tenants from a single database. We needed a strategy to ensure tenant data isolation. Options were: separate databases per tenant, separate schemas per tenant, or shared tables with Row Level Security (RLS).

## Decision

We chose shared tables with PostgreSQL RLS enforced at the database level.

## Consequences

- Isolation enforced at DB level — even a bug in application code cannot leak cross-tenant data
- Single schema to migrate — Alembic migrations apply once, not per tenant
- Lower operational overhead — one database to back up, monitor, and scale
- set_tenant_id() function sets the RLS context per session
- Slightly more complex query setup — every session must call SET LOCAL app.current_tenant_id
- Separate databases would give stronger isolation but at significantly higher operational cost
