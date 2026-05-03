# ADR-002 — Use Clerk for Authentication

## Status

Accepted

## Context

ComplianceKit is multi-tenant — users belong to organisations. We needed auth that handles user login, organisation management, JWT issuance, and webhook events for tenant provisioning. Building this ourselves would take weeks and introduces security risk.

## Decision

We chose Clerk over building our own auth or using Auth0/Cognito.

## Consequences

- Organisation management built-in — maps directly to our tenant model
- JWTs include org_id claim — tenant_id extraction is trivial
- Webhook events (organization.created, user.created) auto-provision tenants in our DB
- JWKS endpoint for JWT verification — no secret sharing needed
- Reduces auth surface area — fewer security vulnerabilities to manage
- Vendor dependency — if Clerk changes pricing or goes down, we're affected
