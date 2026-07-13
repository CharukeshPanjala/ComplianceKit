# ComplianceKit

**B2B SaaS compliance platform for GDPR, NIS2, and EU AI Act.**

ComplianceKit automates the compliance lifecycle for SMEs and mid-market companies. Instead of hiring consultants or manually tracking spreadsheets, a company signs up, completes a 6-step profile, and gets an instant compliance score, a prioritised gap list, AI-drafted policy documents, and a full suite of operational compliance tools.

> Live API: https://api-gateway-production-0bf0.up.railway.app/api/v1/health

---

## What it does

| Module | Description |
|---|---|
| **Compliance Assessment** | 258 regulation rules (GDPR 99 + NIS2 46 + EU AI Act 113) evaluated against company profile. Scores 0-100 per regulation. Gaps ranked by severity and fine exposure. |
| **Gap Management** | Searchable gap list with filters, personalised status explanations, remediation steps, and one-click resolve. |
| **Policy Generation** | AI-drafted Privacy Notice, DPA, Cookie Policy, Data Retention, Incident Response, and AI Governance policies. PDF + DOCX export. |
| **ROPA** | Auto-generated Records of Processing Activities from company profile and tech stack. GDPR Art. 30 compliant. |
| **Vendor Register** | Processor list auto-built from tech stack. DPA status tracking per vendor. |
| **Breach Tracker** | 72-hour GDPR and 24-hour NIS2 countdown. AI-drafted authority notification letters via streaming. |
| **DSAR Management** | 30-day deadline tracking, status workflow, overdue detection, automatic completion timestamp. |
| **DPO Assistant** | Floating AI chat widget on every page. RAG over all 258 embedded regulation articles. Analyse DPA tab for Art. 28 contract review. |
| **Compliance Report** | One-click PDF/DOCX report across all regulations. AI executive summary, gap tables, remediation roadmap. |

---

## Architecture

```
Browser (Next.js 16)
    |
    +-- Clerk (auth + org management)
    |
    +-- API Gateway (FastAPI)   -- company profile, webhooks, auth
    |
    +-- Policy Engine (FastAPI) -- assessments, gaps, policies, ROPA,
             |                     processors, breach, DSAR, DPO assistant,
             |                     compliance report
             |
             +-- ARQ Worker     -- async assessment pipeline (4 DB queries)
             +-- Redis           -- job queue + cache
             +-- PostgreSQL 16   -- 14 tables, Row Level Security per tenant
                  + pgvector     -- 258 embedded regulation articles (RAG)
```

**Multi-tenant isolation:** every table has PostgreSQL Row Level Security. All API requests run as the `app_user` DB role with `SET LOCAL app.current_tenant_id` — no tenant can ever read another tenant's data.

**Prefixed public IDs:** no raw UUIDs in any API response. Every entity uses a nanoid prefix: `ten_`, `usr_`, `asm_`, `gap_`, `pol_`, `ver_`, `dsr_`, `inc_`, `proc_`, `rpa_`, `doc_`.

---

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js 16, TypeScript, Tailwind v4, TanStack Query, Zod, react-hook-form, Recharts, Clerk |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, asyncpg, ARQ, structlog, OpenTelemetry |
| Database | PostgreSQL 16 + pgvector |
| Auth | Clerk (org = tenant, JWT verified offline) |
| AI | Azure OpenAI (EU data residency) - text-embedding-3-small + GPT-4o |
| Infra | Railway (prod), Docker Compose (local), GitHub Actions CI/CD |
| Package managers | uv (Python), pnpm (Node) |

---

## Repo structure

```
ComplianceKit/
  frontend/                   Next.js app
    src/app/(portal)/         Dashboard, Gaps, Policies, ROPA, Vendors,
                              Breach, DSAR, Settings
    src/app/(onboarding)/     6-step onboarding wizard
    src/components/ui/        Shared component library (Badge, GaugeRing,
                              StatCard, EmptyState, CountdownBadge, ...)
    src/lib/hooks/            TanStack Query hooks (20+)

  services/
    api-gateway/              Auth, company profile, Clerk webhooks
    policy-engine/            All compliance features + ARQ worker
    document-generator/       Stub (Sprint 3+)
    dsar-service/             Stub (Sprint 3+)

  packages/
    common/                   Shared SQLAlchemy models, Alembic migrations,
                              auth middleware, logging, OpenTelemetry

  infrastructure/
    docker/                   Docker Compose, Dockerfiles

  docs/                       Architecture diagram, article audit docs, ADRs
```

---

## Local development

### Prerequisites

- Docker Desktop
- Node.js 20+ and pnpm
- Python 3.12 and uv
- A `.env` file (see `.env.example`)

### Start everything

```bash
# Start all backend services (Postgres, Redis, API Gateway, Policy Engine, Worker)
make up

# Run Alembic migrations
make migrate

# Seed all 258 regulation rules
make seed

# Seed pgvector embeddings (requires Azure OpenAI keys)
make seed-embeddings

# Start Next.js dev server
cd frontend && pnpm dev
```

Frontend runs at `http://localhost:3000`. API Gateway at `http://localhost:8000`.

### Useful commands

```bash
make logs           # tail all container logs
make logs-api       # tail api-gateway only
make logs-policy    # tail policy-engine only
make rebuild        # rebuild all containers after Python changes
make rebuild-api    # rebuild api-gateway only
make rebuild-policy # rebuild policy-engine only
make db             # psql shell into Postgres
make test           # run all test suites
make test-api       # api-gateway tests only
make test-common    # common package tests only
```

---

## Environment variables

Create a `.env` file at the repo root. Required variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit
APP_USER_DATABASE_URL=postgresql+asyncpg://app_user:app_user_password@localhost:5432/compliancekit

# Redis
REDIS_URL=redis://localhost:6379

# Clerk
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_WEBHOOK_SECRET=whsec_...
JWT_KEY=-----BEGIN PUBLIC KEY-----...

# Azure OpenAI (optional — stub fallback used when not set)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000
```

---

## Testing

```bash
# All suites
make test

# Individual
uv run pytest services/api-gateway/tests/ -v
uv run pytest services/policy-engine/tests/ -v
uv run pytest packages/common/tests/ -v

# Lint profile field references (CI guardrail)
make lint-fields
```

Current coverage: **475 policy-engine tests + 33 common tests**.

---

## CI/CD

GitHub Actions runs on every PR:

| Check | Tool |
|---|---|
| Python lint | ruff |
| Type check | mypy |
| Tests | pytest |
| Secrets scan | TruffleHog (verified secrets only) |
| Frontend lint | ESLint |
| Frontend types | tsc |

Merging to `main` auto-deploys to Railway. Alembic migrations run as a pre-deploy step.

---

## Database schema

14 tables, all tenant-scoped with RLS:

```
tenants               company identity and billing tier
users                 one row per person, Clerk user_id as PK
company_profiles      compliance posture — input to assessment engine
company_profile_versions  full audit trail of every profile change
regulations           GDPR, NIS2, EU_AI_ACT
regulation_versions   history of regulation changes
rules                 258 rules with fine_tier, severity, check_type
rule_versions         history of rule changes
assessments           one per tenant per regulation per run
gaps                  one per rule per assessment
policies              compliance documents (Privacy Notice, DPA, etc.)
policy_versions       full version history
dsar_requests         Data Subject Access Request lifecycle
breach_incidents      breach notification tracker
processors            vendor / data processor register
ropa_entries          Records of Processing Activities
documents             generated PDFs/DOCX
```

---

## Key design decisions

See `docs/` for the full Architecture Decision Records. Quick summary:

- **FastAPI** over Django — async-native, automatic OpenAPI docs
- **Clerk** for auth — org primitives map directly to tenants, no custom auth code
- **PostgreSQL RLS** for multi-tenancy — enforced at DB level, impossible to bypass in application code
- **Railway** for hosting — Git-native deploy, managed Postgres and Redis
- **uv** for Python — 10-100x faster than pip, lockfile-based reproducibility
- **ARQ** for async jobs — assessment pipeline runs in a separate worker process, API returns 202 immediately
- **Azure OpenAI** — EU data residency required for GDPR compliance of the platform itself

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Commit format: `type(scope): description (COM-xxx)`.

Allowed scopes: `gateway`, `policy`, `docs`, `dsar`, `common`, `frontend`, `infra`, `ci`, `deps`, `release`, `db`.
