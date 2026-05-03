# ComplianceKit — System Architecture

![Architecture Diagram](./architecture.png)

## Diagram

```mermaid
flowchart TD
    User["Browser / User"]

    User -->|HTTPS| Clerk
    User -->|HTTPS| Frontend

    Clerk["Clerk\nAuth + Org management"]
    Frontend["Frontend\nNext.js 16 + Tailwind"]

    Clerk -->|JWT| Frontend
    Clerk -->|webhook| Gateway

    Frontend -->|API calls| Gateway

    Gateway["API Gateway\nFastAPI · JWT verify · RLS · Logging · Tracing"]

    Gateway --> PolicyEngine
    Gateway --> DocGenerator
    Gateway --> DSAR
    Gateway -->|cache| Redis

    PolicyEngine["Policy Engine\nGDPR · NIS2 · AI Act"]
    DocGenerator["Doc Generator\nReports + templates"]
    DSAR["DSAR Service\nData subject requests"]

    PolicyEngine --> Postgres
    DocGenerator --> Postgres
    DSAR --> Postgres
    DSAR --> Redis

    Postgres[("PostgreSQL 16\nRLS · Multi-tenant · Alembic")]
    Redis[("Redis 7\nCache + sessions")]

    subgraph Infra["Infrastructure + External"]
        Railway["Railway"]
        GHA["GitHub Actions"]
        OpenAI["OpenAI API"]
        GHCR["GHCR"]
    end
```

## Services

- **API Gateway** — main entry point, handles auth, RLS, logging, tracing
- **Policy Engine** — GDPR, NIS2, AI Act compliance rules
- **Document Generator** — compliance reports and templates
- **DSAR Service** — data subject access requests

## Infrastructure

- **Railway** — production hosting
- **GitHub Actions** — CI/CD pipelines
- **GHCR** — container registry
- **OpenAI API** — AI features (Sprint 1+)
