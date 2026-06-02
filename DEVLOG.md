# ComplianceKit — Dev Log

Running diary of progress, decisions, and blockers across all sprints.
Updated every time a ticket is closed.

---

---

## Sprint 0 — Foundation

**Goal:** Get the monorepo scaffolded, documented, and pushed to GitHub. No application code yet — just structure, tooling config, and conventions.

---

### Epic 0.1 — Monorepo Setup (COM-1)

Foundation sprint — set up the entire project structure, tooling, and conventions before writing any application code.

### COM-142 — Create monorepo folder structure ✅

**Date:** April 12, 2025
**Status:** Done

**What I did:**

- Scaffolded the full monorepo from scratch using terminal commands
- Created 4 service skeletons: `api-gateway`, `policy-engine`, `document-generator`, `dsar-service`
- Each service has the standard FastAPI layout: `app/{api,core,models,schemas,services}/` + `tests/`
- Created `packages/common/` as a shared Python library (db, auth, middleware, utils, schemas)
- Created `frontend/` skeleton for Next.js 14 (app, components, lib, types, public)
- Created `infrastructure/` with docker, railway, scripts, and terraform subfolders
- Created `docs/adr/` with 3 initial ADRs and a template
- Created `.github/workflows/` with stub `ci.yml` and `deploy.yml`
- Added root files: `.gitignore`, `.env.example`, `docker-compose.yml`, `README.md`, `CONTRIBUTING.md`, `CODEOWNERS`
- 44 files created, committed, and pushed to GitHub

**Structure:**

```
compliancekit/
├── services/
│   ├── api-gateway/
│   ├── policy-engine/
│   ├── document-generator/
│   └── dsar-service/
├── packages/common/
├── frontend/
├── infrastructure/
├── docs/adr/
├── .github/workflows/
├── README.md
├── CONTRIBUTING.md
└── CODEOWNERS
```

**Decisions made:**

- Used flat `services/` layout over Turborepo — simpler for a Python-heavy stack, Turborepo's build graph optimisation only pays off with many frontend packages
- Kept `infrastructure/` centralised rather than per-service — makes infra changes reviewable in one place via CODEOWNERS
- Each service has its own `pyproject.toml` so dependencies can be pinned independently
- `packages/common` is a library (imported at build time), not a deployed service — avoids a shared-service single point of failure
- PostgreSQL RLS chosen for tenant isolation (ADR-0003) — defence-in-depth, a compromised service still cannot leak cross-tenant data
- Clerk chosen for auth (ADR-0002) — org/role primitives map directly to multi-tenancy model
- FastAPI over Django (ADR-0001) — async-native, automatic OpenAPI, better type-hint integration

**Blockers hit + fixes:**

- zsh choked on `#` comment lines when pasting the full script block — fixed by running heredoc blocks separately
- `git branch -M main` threw an error because repo was already on main — harmless, ignored
- `gh` CLI not installed — pushed manually: `git remote add origin` + `git push -u origin main`
- `zsh: missing delimiter for 'g' glob qualifier` on heredoc — re-ran the `.gitignore` heredoc block in isolation

**Resources:**

- [FastAPI project structure docs](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [ADR concept — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Conventional Commits spec](https://www.conventionalcommits.org/en/v1.0.0/)

---

| Topic                  | Decision                | Rationale                                     |
| ---------------------- | ----------------------- | --------------------------------------------- |
| Monorepo style         | Flat `services/` layout | Simpler than Turborepo for Python-heavy stack |
| Auth                   | Clerk                   | Org/role primitives fit multi-tenancy         |
| DB isolation           | PostgreSQL RLS          | Defence-in-depth — app layer + DB layer       |
| Backend framework      | FastAPI                 | Async-native, OpenAPI, type hints             |
| Python package manager | `uv`                    | 10-100x faster than pip, lockfile-based       |
| Node package manager   | `pnpm`                  | Strict mode, no phantom dependencies          |
| Deployment             | Railway                 | Per-service deploy model fits microservices   |
| Commit format          | Conventional Commits    | Feeds automated changelog + semver            |
| Branch strategy        | Trunk-based off `main`  | Linear history, short-lived branches          |

## Upcoming

### COM-3 — (next ticket title here)

What I did:
Installed uv, created root pyproject.toml declaring uv workspace with 5 members,
restructured packages/common into correct Python package layout, added pyproject.toml
to all four services. uv sync runs cleanly, import common works.

Decisions made:

- Used hatchling as build backend — modern, fast, well supported by uv
- packages = ["app"] explicitly declared in each service — hatchling can't auto-detect
  because folder is named app/ not api_gateway/
- Dev dependencies declared once at root — not repeated per service

Blockers hit + fixes:

- hatchling failed to build services — missing packages = ["app"] in each
  service's [tool.hatch.build.targets.wheel]. Fixed by adding that line to all four.

### COM-4 — Set up Node.js workspace with pnpm ✅

**Date:** April 12, 2026
**Status:** Done

**What I did:**

- Installed pnpm (already present at v10.4.0)
- Created pnpm-workspace.yaml at repo root declaring frontend and dsar-workflow as packages
- Added package.json to frontend with Next.js 14, Clerk, Tailwind, TypeScript
- Created dsar-workflow stub package
- 394 packages installed successfully

**Decisions made:**

- Using TypeScript across the entire frontend
- dsar-workflow kept as empty stub for now — will be populated in later sprint

**Blockers hit + fixes:**

- Network timeout on network — fixed by forcing IPv4 via pnpm config set prefer-ip-version ipv4

---

### COM-5 — Configure Git — .gitignore, branch protection, commit conventions ✅

**Date:** April 12, 2026
**Status:** Done

**What I did:**

- Updated .gitignore to cover Python, Node, Docker, OS and IDE files
- Added PR template and bug report issue template in .github/
- Set up commitlint + husky to enforce conventional commits locally
- Made repo public to enable branch protection on main
- Branch protection rule set on main — PRs required, force push blocked

**Decisions made:**

- Made repo public — only way to get branch protection on free GitHub plan
- Kept branch protection simple — no required approvals since solo project
- One-liner commits are fine for straightforward tasks

**Blockers hit + fixes:**

- GitHub Rulesets don't enforce on private repos without Team plan
- Fixed by making repo public and using Branch Protection Rules instead

### Epic 0.2 — Local Development Environment (COM-6)

Get the full stack running locally with one command — Docker, databases, and all services up and healthy.

### COM-7 — Docker Compose with Postgres, Redis, and service stubs ✅

**Date:** April 12, 2026
**Status:** Done

**What I did:**

- Created infrastructure/docker/docker-compose.yml with Postgres 16, Redis 7 and stub containers for all 4 services
- Added persistent volumes so data survives restarts
- Added healthchecks so services wait for Postgres and Redis to be ready before starting
- Verified Postgres and Redis are reachable from Mac

**Decisions made:**

- Service stubs use python:3.12-slim with time.sleep(86400) — keeps container alive without real app code
- Volumes named postgres_data and redis_data — managed by Docker, not host paths

**Blockers hit + fixes:**

- time.sleep(infinity) — infinity is not a Python built-in, fixed with time.sleep(86400)

---

### COM-8 — Environment variable management ✅

**Date:** April 14, 2026
**Status:** Done

**What I did:**

- Created .env.example with all required variables and placeholder values
- Created .env locally with real values (not committed)
- Added pydantic-settings to packages/common
- Created BaseServiceSettings in common/config.py — shared by all services
- Each service has its own config.py extending BaseServiceSettings
- Verified service refuses to start with clear error when DATABASE_URL is missing

**Decisions made:**

- ROOT_DIR uses parents[3] to locate .env from anywhere in the repo
- BaseServiceSettings in common — shared base, each service extends with its own extras later
- database_url has no default — forces explicit configuration, no silent failures

**Blockers hit + fixes:**

- Pydantic validation not triggering with empty .env — fixed by deleting .env entirely to confirm fail-fast works
- PATH calculation wrong (parents[4]) — fixed to parents[3] matching actual folder depth

### COM-9 — Alembic migrations and seed script ✅

**Date:** April 15, 2026
**Status:** Done

**What I did:**

- Added Alembic, SQLAlchemy asyncio, asyncpg, nanoid to packages/common
- Created tenants and users SQLAlchemy models with enums for plan and role
- Added prefixed public IDs (ten_xxxxxxxx, usr_xxxxxxxx) for API safety
- Initialised Alembic and configured async env.py
- Generated and ran migration — tenants and users tables created in Postgres
- Created seed script that inserts test tenant (Acme GmbH) and admin user

**Decisions made:**

- Separate internal UUID (id) from public prefixed ID (tenant_id, user_id) — never expose raw UUIDs in API
- Used enums for plan and role — prevents invalid values at DB level
- updated_at on both tables — audit trail for compliance platform
- Seed script in Python not shell — uses SQLAlchemy directly, type safe

**Blockers hit + fixes:**

- utils folder created at wrong level (packages/common/utils instead of packages/common/common/utils) — moved to correct location
- **init**.py named incorrectly as **init.py** — renamed

### COM-10 — Add /health endpoints to all FastAPI services ✅

**Date:** April 16, 2026
**Status:** Done

**What I did:**

- Added /health endpoint to all four services returning {"status": "ok", "service": "..."}
- Wrote real Dockerfiles for each service replacing sleep stubs from COM-7
- Added curl to python:3.12-slim images for Docker health checks
- Wired healthchecks in docker-compose.yml — all 6 containers show healthy
- Generated uv.lock at repo root and copied into each Dockerfile

**Decisions made:**

- curl installed via apt in each Dockerfile — needed for Docker health check command
- start_period: 10s gives services time to boot before health checks begin
- uv.lock copied from repo root — single lockfile for the whole workspace

**Blockers hit + fixes:**

- uv sync --frozen failed — no uv.lock per service. Fixed by running uv lock at root and copying it in each Dockerfile
- Containers showed unhealthy despite working — curl not installed in slim image. Fixed by adding apt-get install curl to each Dockerfile

### COM-12 — Design the multi-tenant database schema ✅

**Date:** April 17, 2026
**Status:** Done

**What I did:**

- Designed all 14 tables covering the full ComplianceKit platform
- Researched actual GDPR (99 articles), NIS2 (Articles 20, 21, 23), and EU AI Act articles to ensure complete coverage
- Created Mermaid ERD diagram with full table and column descriptions
- Saved to docs/schema.md — renders on GitHub automatically
- Created COM-143 — regulatory transparency page (future ticket)

**Tables designed:**
tenants, users, company_profiles, company_profile_versions,
regulations, regulation_versions, rules, rule_versions,
assessments, gaps, policies, policy_versions,
dsar_requests, documents

**Decisions made:**

- JSONB for regulation-specific profile data — no migrations when adding new regulations
- Generic regulations/rules/assessments/gaps design — one set of tables handles GDPR, NIS2, AI Act and any future regulation
- Version history at every level — company profiles, regulations, rules, policies all have version tables
- Prefixed public IDs — ten_xxx, usr_xxx, pol_xxx etc — raw UUIDs never exposed
- regulation_version_id stamped on assessments and gaps — legally defensible, historical records never change
- accepted_risk on gaps — formal risk acceptance with reason and expiry date
- Denormalised tenant_name, regulation_name on child tables — fast queries, no joins for common display fields
- Separated tenants (identity/billing) from company_profiles (compliance data) — different change frequencies, different audit requirements

**Blockers: None**

### COM-13 — Implement Row Level Security ✅

Date: April 18, 2026
Status: Done

What was done:

- Alembic migration enables RLS on tenants and users tables
- set_tenant_id() PostgreSQL function created
- app_user role created — non-superuser, RLS enforced
- Test infrastructure built: conftest.py with session-scoped fixtures
- 3 tests passing — cross-tenant isolation confirmed

Test structure:
packages/common/
tests/
conftest.py ← setup_app_role, db_session, app_session, two_tenants
unit/
test_rls.py ← TestRLS class with 3 tests

Decisions made:

- app_user in conftest not migration — test concern
- Session scoped fixtures — one event loop for all fixtures and tests
- NullPool — no connection pooling in tests
- Delete teardown — RLS tests need committed data, rollback won't work
- asyncio_default_test_loop_scope = session — critical fix for event loop mismatch
- Option B guard in setup_app_role — checks information_schema.role_table_grants before setup

Blockers: None

### COM-16 — Create and configure Clerk account + application ✅

Date: April 19, 2026
Status: Done

What was done:

- Created Clerk account and ComplianceKit application
- Enabled Google + Email/Password as sign-in methods
- Enabled Organizations with Membership Required
  → one Clerk org = one tenant in ComplianceKit
  → no orphaned users without a tenant
- Copied API keys to frontend/.env.local and root .env
- Updated .env.example with placeholder values

Decisions made:

- Membership Required — pure B2B, every user must belong to a company
- Email + Google only — standard B2B combination, no consumer platforms
- Microsoft/Azure AD deferred — worth adding later for enterprise customers

Blockers: None

### COM-17 — Add Clerk auth to the Next.js frontend ✅

Date: April 19, 2026
Status: Done

What was done:

- Upgraded Next.js 14 → 16.2.4
- Upgraded Node.js 18 → 20.20.2 (required for Next.js 16)
- Upgraded Tailwind v3 → v4
- Upgraded ESLint 8 → 10
- Added src/ folder structure
- Created full app folder structure with route groups:
  (public), (auth), (onboarding), (portal)
- Installed and configured ClerkProvider in root layout.tsx
- Created sign-in and sign-up pages using Clerk components
- Created proxy.ts middleware protecting all portal routes
- Verified auth flow end to end

Decisions made:

- src/ folder — cleaner separation of source vs config files
- Route groups — (public), (auth), (onboarding), (portal)
  each with their own layout
- Option C structure — regulation-specific overview pages,
  shared filterable pages for gaps/assessments/policies
- (portal) instead of (app) or (dashboard) — more professional
  for a B2B compliance product
- middleware.ts renamed to proxy.ts — Next.js 16 requirement
- Tailwind v4 — no config file needed, cleaner setup
- typedRoutes at top level — moved out of experimental in Next.js 16

Pages structure:
(public) → /, /pricing, /about, /contact
(auth) → /sign-in, /sign-up
(onboarding) → /onboarding
(portal) → /dashboard, /gdpr, /nis2, /ai-act,
/gaps, /assessments, /policies,
/dsar, /settings

Verified:

- /sign-in → Clerk sign in page ✅
- /sign-up → Clerk sign up page ✅
- /dashboard (not logged in) → redirects to /sign-in ✅
- Sign up → redirects to /dashboard ✅
- Company logo stored in Clerk, not our DB ✅

Blockers: None

## Notes & Ongoing Decisions

### COM-18 — Verify Clerk JWT tokens in FastAPI backend ✅

Date: April 19, 2026
Status: Done

What was done:

- Created common/auth/clerk.py with verify_token() FastAPI dependency
- Created TokenClaims Pydantic model — user_id, tenant_id, org_role
- JWKS fetching with caching — Clerk's public keys fetched once, cached
- 4 unit tests passing — valid token, expired, invalid, no org

Decisions made:

- PyJWT + httpx — lightweight, no heavy Clerk Python SDK needed
- JWKS caching — avoids fetching Clerk's public keys on every request
- org_id as tenant_id — Clerk org maps directly to our tenant
- 401 for missing org — user must belong to an org, personal accounts not allowed
- Mocking in tests — no real Clerk tokens needed, fast and reliable

Files created:
packages/common/common/auth/**init**.py
packages/common/common/auth/clerk.py
packages/common/tests/unit/test_clerk_auth.py

Test results: 4 passed

Blockers: None

### COM-19 — Auto-provision tenant on Clerk webhook ✅

Date: April 24, 2026
Status: Done

What was done:

- Created packages/common/common/db/session.py — shared async SQLAlchemy
  session factory (admin, no RLS scoping)
- Created packages/common/common/db/**init**.py
- Rewrote services/api-gateway/app/api/v1/endpoints/webhooks.py —
  real DB inserts replacing print() stubs
- Added clerk_webhook_secret to GatewaySettings
- Added env_file to all 4 services in docker-compose.yml
- Fixed DATABASE_URL to use compliancekit-postgres (Docker hostname)
- Installed ngrok, wired to Clerk webhook dashboard for local testing
- Verified end-to-end: Clerk test event → tenant row in PostgreSQL
- Added 5 unit tests — all passing

Decisions made:

- Admin DB session in common/db/ — all services will need DB access
- No RLS on webhook session — server-to-server call, no tenant context yet
- Duplicate guard via slug lookup — silent skip if org already exists
- First user in an org always gets ADMIN role

Blockers hit + fixes:

- Docker containers had no env vars — added env_file to docker-compose.yml
- DATABASE_URL used localhost — fixed to container hostname
- Volumes wiped when containers deleted — re-ran alembic upgrade head
- app.api.v1 not resolving in tests — fixed with pythonpath = ["."] in pyproject.toml

### COM-14 — Write TenantMiddleware for FastAPI ✅

Date: April 24, 2026
Status: Done

What was done:

- Created packages/common/common/db/tenant.py — get_tenant_session()
  FastAPI dependency
- Chains verify_token() → opens DB session → SET LOCAL app.current_tenant_id
- RLS activates automatically for all routes using this dependency
- Updated common/db/**init**.py to export get_tenant_session
- 3 unit tests passing

Decisions made:

- Dependency injection over middleware — idiomatic FastAPI, testable,
  no streaming issues
- SET LOCAL inside transaction — resets after request, safe for
  connection pooling
- Health routes excluded automatically — dependency applied at router
  level, not globally

Blockers: None

### COM-21 — GitHub Actions: automated test pipeline on every PR ✅

Date: April 25, 2026
Status: Done

What was done:

- Created .github/workflows/ci.yml with Python and Frontend jobs
- Python job: ruff lint → mypy → alembic migrations → pytest
- Frontend job: disabled until real frontend code exists
- Fixed 9 ruff lint errors — unused imports and variables
- Added mypy config to root pyproject.toml
- Fixed pnpm cache path in CI
- Added migration step so set_tenant_id() exists in CI DB

Decisions made:

- mypy Option 2 — override config files only, not full pydantic plugin
- Frontend CI disabled — pointless to lint/typecheck a skeleton
- Only testing common + api-gateway — other services have no tests yet

Skipped for future:

- Frontend lint/typecheck — re-enable at COM-71
- Playwright E2E in CI — when first E2E tests written
- pytest-cov coverage threshold — add in observability sprint
- mypy pydantic plugin — upgrade when codebase more stable
- Matrix Python version testing — not needed at this stage

Blockers hit + fixes:

- pnpm cache path wrong — fixed to root pnpm-lock.yaml
- set_tenant_id() missing in CI DB — added alembic upgrade head step
- mypy false positives — added module overrides for config files
- ruff caught 9 real issues — all fixed

Next: COM-22 — Build and push Docker images on merge to main

### COM-22 — GitHub Actions: build and push Docker images on merge to main ✅

Date: April 25, 2026
Status: Done

What was done:

- Created .github/workflows/deploy.yml
- Matrix strategy builds all 4 services in parallel
- Images pushed to GHCR with latest + sha tags
- Uses built-in GITHUB_TOKEN — no secrets setup needed
- Verified — 4 packages visible on GitHub

Decisions made:

- GHCR over Docker Hub — free, no rate limits, built into GitHub
- Matrix strategy — avoids copy-pasting steps 4 times
- Both latest + SHA tags — latest for convenience, SHA for rollback

Blockers hit + fixes:

- Invalid action input dockerfile — fixed to file parameter

Next: COM-23 — Set up Railway project

### COM-23 — Set up Railway project with Postgres, Redis, and GitHub auto-deploy ✅

Date: May 3, 2026
Status: Done

What was done:

- Created Railway project (compliance-kit)
- Added managed Postgres and Redis services
- Connected GitHub repo — push to main triggers auto-deploy
- Switched from GHCR Docker image deployment to GitHub source deployment
- Railway builds directly from our Dockerfiles on every push to main
- Added railway.toml config as code for api-gateway
- Fixed alembic/env.py to read DATABASE_URL from environment
- Fixed Dockerfiles to use ${PORT:-8000} for Railway port compatibility
- Added PORT=8000 variable to align Railway proxy with Uvicorn
- Pre-deploy command runs alembic migrations before every deploy
- Healthcheck configured at /api/v1/health
- api-gateway live at: https://api-gateway-production-0bf0.up.railway.app

Decisions made:

- GitHub source over GHCR images — railway.toml works, pre-deploy reliable
- PORT=8000 explicitly set — Railway injects PORT but proxy needs alignment
- Disabled COM-22 deploy workflow — Railway handles builds directly now
- Pre-deploy via railway.toml array format — single sh -c element

Skipped / deferred:

- policy-engine, document-generator, dsar-service deployment — stubs, no real code
- Serverless on stub services — do when deploying remaining services
- Postgres daily backups — set up in observability sprint
- Wait for CI — enable when Railway GitHub integration is stable
- Custom domain — needed when we have real customers

Blockers hit + fixes:

- railway.toml ignored for Docker image deployments — switched to GitHub source
- Pre-deploy cd command failed — no shell in exec form, fixed with sh -c
- preDeployCommand array limited to 1 element — combined into single sh -c string
- alembic.ini hardcoded localhost — fixed env.py to read DATABASE_URL from env
- Healthcheck failing — app hardcoded port 8000, Railway injected 8080 — fixed with PORT=8000 variable
- railway.toml skipped — set config file path in Railway dashboard settings

Next: COM-24

### COM-24 — Add all production environment variables to Railway ✅

Date: May 3, 2026
Status: Done

What was done:

- Added railway.toml for policy-engine, document-generator, dsar-service
- Each stub service has healthcheck, restart policy configured
- Added CLERK_SECRET_KEY and CLERK_PUBLISHABLE_KEY to api-gateway in Railway
- Added DATABASE_URL, REDIS_URL, ENVIRONMENT, PORT to all stub services
- Connected policy-engine and document-generator to GitHub source in Railway
- Set config file path for each service in Railway dashboard

Decisions made:

- Stub services use /health not /api/v1/health — simpler endpoint, no router
- healthcheckTimeout 60s for stubs — they start faster than api-gateway
- OpenAI key deferred — not used in any code yet, add in Sprint 1
- DEBUG not set explicitly — defaults to False in BaseServiceSettings

Blockers: None

### COM-26 — Structured JSON logging with tenant and request context ✅

Date: May 3, 2026
Status: Done

What was done:

- Added structlog to packages/common dependencies
- Created common/log_config.py — configures structlog:
  - Production: JSON output (searchable in Railway)
  - Development: coloured pretty output
- Created common/middleware/request_logger.py — LoggingMiddleware:
  - Generates unique request_id (UUID) per request
  - Binds tenant_id, user_id, org_role, method, path to every log line
  - Adds X-Request-ID to response headers
- Updated get_tenant_session() in common/db/tenant.py:
  - Sets request.state.tenant_id, user_id, org_role after JWT verification
  - Logging middleware picks these up automatically
- Wired LoggingMiddleware into api-gateway main.py
- 6 new tests, 16 total passing

Log format (development):
2026-05-03T18:39:21Z [info] request_started [common.middleware.request_logger]
method=GET path=/api/v1/health request_id=ac3ceb19... tenant_id=anonymous

Log format (production):
{"level": "info", "tenant_id": "ten_xxx", "request_id": "abc-123", "message": "request_started"}

Decisions made:

- stdlib LoggerFactory over PrintLoggerFactory — needed for add_logger_name processor
- org_role added to log context — useful for debugging permission issues
- request.state set in get_tenant_session — single source of truth for auth context
- Docker port conflict caused debugging delay — local testing must use non-Docker ports

Blockers hit + fixes:

- Port 8000 conflict with Docker — fixed by running uvicorn on port 8080 locally
- structlog add_logger_name incompatible with PrintLoggerFactory — switched to stdlib LoggerFactory
- Test used VALID_CLAIMS instead of loop claims — fixed

Next: COM-27 — Instrument FastAPI with OpenTelemetry tracing

### COM-27 — Instrument FastAPI with OpenTelemetry tracing ✅

Date: May 3, 2026
Status: Done

What was done:

- Added opentelemetry-sdk, opentelemetry-instrumentation-fastapi,
  opentelemetry-instrumentation-sqlalchemy, opentelemetry-exporter-otlp
  to packages/common dependencies
- Created common/tracing.py — configure_tracing() and get_tracer()
- Wired FastAPIInstrumentor and SQLAlchemyInstrumentor into api-gateway main.py
- ConsoleSpanExporter outputs traces to stdout for now
- 5 unit tests passing
- Verified end-to-end: traces appear in logs with trace_id, span_id,
  http.method, http.route, http.status_code, duration

Trace output verified:
{
"name": "GET /api/v1/health",
"trace_id": "0x395d2f07e42db1874f678ebe8cde1cb0",
"kind": "SpanKind.SERVER",
"http.method": "GET",
"http.route": "/api/v1/health",
"http.status_code": 200,
"service.name": "api-gateway"
}

Decisions made:

- ConsoleSpanExporter for now — swap for OTLPSpanExporter later
- opentelemetry-exporter-otlp added now — ready for future dashboard integration
- Resource includes service.name and deployment.environment per service
- Tests use Resource directly — OpenTelemetry doesn't allow resetting global
  provider between tests

Deferred:

- Shipping traces to Jaeger/Honeycomb/Grafana Tempo — future observability ticket
- Wiring tracing into other 3 services — when they have real code

Next: COM-29 — System architecture diagram

### COM-30 — Draw the system architecture diagram ✅

Date: May 3, 2026
Status: Done

What was done:

- Created docs/architecture.md with Mermaid source diagram
- Saved docs/architecture.png for README embedding
- Embedded diagram in README.md
- Diagram shows full system: Browser → Clerk + Frontend →
  API Gateway → Policy Engine + Doc Generator + DSAR Service
  → PostgreSQL + Redis
- External infra section: Railway, GitHub Actions, OpenAI API, GHCR
- Color coded by layer: Gateway (blue), Services (coral),
  Database (green), Auth (purple), Frontend (teal), Infra (gray)

Decisions made:

- Mermaid as source of truth — stays in repo, renders on GitHub
- PNG for README and academic submission
- DSAR → Redis connection included — DSAR needs queuing
- API Gateway → Redis shown as cache connection (dashed)
- OpenAI in infra section — not yet implemented, planned Sprint 1

### COM-31 — Write Architecture Decision Records (ADR-001 to ADR-010) ✅

Date: May 3, 2026
Status: Done

What was done:

- Filled in existing ADR-001, ADR-002, ADR-003 (were empty placeholders)
- Created 7 new ADRs covering all Sprint 0 decisions
- All 10 ADRs saved in docs/adr/

ADRs written:

- ADR-001 — FastAPI over Django
- ADR-002 — Clerk for authentication
- ADR-003 — PostgreSQL RLS for multi-tenancy
- ADR-004 — Railway over AWS/Heroku
- ADR-005 — Monorepo over separate repos
- ADR-006 — uv over pip/poetry
- ADR-007 — structlog for structured logging
- ADR-008 — OpenTelemetry for tracing
- ADR-009 — GitHub source deployment over GHCR images
- ADR-010 — Async SQLAlchemy over sync

Each ADR covers: Status, Context, Decision, Consequences.

## Pre-Sprint 1 — Security & Reliability Fixes

**Date:** May 10, 2026
**Status:** Done

**What was done:**

- Added `clerk_org_id` to `tenants` and `clerk_user_id` to `users` — Alembic migration + SQLAlchemy models updated
- Created `app_user` PostgreSQL role in migration with correct grants so `FORCE ROW LEVEL SECURITY` is enforced in production (previously bypassed — superuser connection skips RLS)
- Switched Clerk webhook tenant/user lookup from slug to `clerk_org_id` — slug can change in Clerk, org ID is immutable
- Replaced forever-cached JWKS dict with 1-hour `TTLCache` + one retry on `InvalidTokenError` to handle Clerk key rotation without a service restart
- Fixed `LoggingMiddleware` to bind `tenant_id`/`user_id` after `call_next()` so `request_completed` log has real context instead of `"anonymous"`

**Decisions made:**

- `cachetools.TTLCache` over manual timestamp tracking — simpler, thread-safe
- Retry-once pattern on `InvalidTokenError` — handles mid-rotation window without hammering Clerk's JWKS endpoint
- `app_user` created in migration not conftest — production concern, not a test concern

**Blockers: None**

**Hotfix — May 14, 2026**

- Fixed `GRANT CONNECT ON DATABASE` hardcoded `compliancekit` name — Railway's DB has a different name. Switched to `DO $$ EXECUTE 'GRANT/REVOKE CONNECT ON DATABASE ' || current_database() ...`
- Fixed `downgrade()` missing `REVOKE EXECUTE ON FUNCTION set_tenant_id(TEXT)` — Postgres refused to drop `app_user` while the function grant still existed

## Sprint 1 — Company Profile & Onboarding

### COM-130 — DB tables + Alembic migration ✅

**Date:** May 14, 2026
**Status:** Done

**What was done:**

- Added `gdpr_enabled`, `nis2_enabled`, `ai_act_enabled` boolean columns to `tenants` table
- Created `company_profiles` table with all columns including `tech_stack` JSONB
- Created `company_profile_versions` table for full audit trail
- Enabled RLS on both new tables with `tenant_isolation` policy
- Granted `app_user` access to both new tables
- Added `generate_profile_id()` (`cp_`) and `generate_profile_version_id()` (`cpv_`) to `ids.py`
- Created `CompanyProfile` and `CompanyProfileVersion` SQLAlchemy models
- Added `Industry`, `CompanySize`, `B2BOrB2C`, `NumberOfDataSubjects` enums
- Updated `SCHEMA.md` to reflect `cp_` prefix

**Decisions made:**

- `tech_stack` added as JSONB — needed for onboarding wizard step 2 (COM-137)
- Regulation toggles as boolean columns (`gdpr_enabled` etc.) not JSONB — simpler and fast to query
- All new fields on `company_profiles` nullable — profile is built incrementally during onboarding, not all at once
- `company_profile_versions` has no `updated_at` — rows are write-once, never updated

**Blockers: None**

### COM-133 — Unit + integration + RLS tests ✅

**Date:** May 14, 2026
**Status:** Done

**What was done:**

- Created `test_company_profile.py` — 6 unit tests for model IDs, defaults and structure
- Created `test_rls_company_profile.py` — 3 RLS integration tests proving tenant isolation on company_profiles
- All 30 tests passing

**Decisions made:**

- `assert not profile.is_complete` instead of `assert profile.is_complete is False` — SQLAlchemy defaults only apply at DB insert time, not object instantiation
- Separate fixture `two_tenant_profiles` — keeps RLS test data isolated from the existing `two_tenants` fixture

**Blockers: None**

## 2026-05-14 — COM-131: Company Profile API

**Branch:** `feat/COM-131-company-profile-api`

### What was built

- `services/api-gateway/app/api/v1/schemas/profile.py` — Pydantic v2 schemas: `ProfileCreate`, `ProfileUpdate`, `ProfileResponse`
- `services/api-gateway/app/api/v1/endpoints/profile.py` — Three endpoints:
  - `POST /api/v1/profile` — creates profile for tenant (409 if exists)
  - `GET /api/v1/profile` — returns current tenant's profile (404 if not found)
  - `PATCH /api/v1/profile` — saves a `CompanyProfileVersion` snapshot before applying updates
- Wired profile router into `app/api/v1/router.py`
- `services/api-gateway/tests/test_profile.py` — 6 unit tests covering all endpoints and error paths

### Key decisions

- All profile fields optional — built incrementally during onboarding wizard
- PATCH saves a version snapshot first so the full audit trail is preserved before any field changes
- `session.add = MagicMock()` in test fixture because SQLAlchemy's `add()` is synchronous (AsyncMock produces unawaited coroutine warnings

## 2026-05-15 — COM-132: SaaS Tools Registry

**Branch:** `feat/COM-132-saas-tools`

### What was built

- `packages/common/common/models/saas_tool.py` — `SaasTool` model (global, no RLS)
- Alembic migration — creates `saas_tools` table and seeds 200 tools across 26 categories
- `services/api-gateway/app/api/v1/schemas/tool.py` — `ToolCreate`, `ToolResponse`
- `services/api-gateway/app/api/v1/endpoints/tools.py` — `GET /api/v1/tools` (list + category filter), `POST /api/v1/tools` (add custom tool, case-insensitive dedup)
- `services/api-gateway/tests/test_tools.py` — 6 tests

### Key decisions

- 200 tools seeded across 26 categories — cloud, payments, CRM, HR, EOR, security, analytics and more
- `POST /tools` is idempotent — duplicate names return existing tool rather than erroring
- No DELETE/PATCH — global reference data, admin-only via DB
- `is_active` flag allows hiding tools without deleting them

### Fix: OTEL logging errors in tests

- `ConsoleSpanExporter` + `BatchSpanProcessor` caused background thread crash after pytest closed stdout
- Fixed `packages/common/common/tracing.py` to only attach an exporter when `OTEL_EXPORTER_OTLP_ENDPOINT` is set
- Dev/test runs with no exporter — no background thread, clean test output

### COM-133 — Write unit and integration tests for the company profile API ✅

**Date:** May 14–20, 2026
**Status:** Done

**What was done:**

- Created `test_company_profile.py` — 6 unit tests for model IDs, defaults and structure
- Created `test_rls_company_profile.py` — 4 RLS integration tests proving tenant isolation
  on `company_profiles` and `company_profile_versions`
- Expanded `test_webhooks.py` — 11 new tests covering `organizationMembership.created`
  handler (all edge cases: missing keys, empty IDs, duplicate guard, role mapping)
- Added `test_user_created_empty_email_addresses_returns_200` — regression test for
  IndexError bug fixed during Clerk integration
- Expanded `test_profile.py` — 3 new tests: POST with no body → 201, PATCH invalid
  enum → 422, PATCH invalid data_role → 422
- Added `test_tools.py` — POST with no name → 422
- Expanded `test_clerk_auth.py` — 2 new tests: legacy `org_id` field fallback,
  `o.id` takes priority over `org_id`
- Rewrote `test_clerk_auth.py` — old tests patched `_get_jwks` which no longer exists;
  rewritten to mock `_clerk.authenticate_request` matching current SDK implementation
- Fixed `test_profile.py` mocks — added `data_role = None` to `make_mock_profile()`
  and `fake_refresh()` functions (Sprint 1 field added, tests not updated)
- Fixed `test_rls_company_profile.py` — removed `generate_tenant_id` import
  (function deleted when switching to Clerk IDs)
- Added `--import-mode=importlib` to root `pyproject.toml` — resolves conftest
  naming conflict when running both test suites
- Created `Makefile` at repo root — `make test`, `make test-api`, `make test-common`,
  `make up/down/rebuild/logs` for all services individually

**Test results:** 64 passed (31 api-gateway + 33 common)

**Decisions made:**

- Separate `make test-api` and `make test-common` — different pytest configs
  (asyncio AUTO vs STRICT), must run from different rootdirs
- `&&` in `make test` — fail fast, second suite only runs if first passes

**Blockers: None**

---

### Clerk Integration Fixes & End-to-End Onboarding — May 19-20, 2026

**Status:** Done

---

#### Fix: Clerk IDs too long for VARCHAR(20)

**Problem:** `StringDataRightTruncationError` — Clerk org IDs are 31 chars,
columns were VARCHAR(20).

**Root cause (deeper):** DB was storing internal `ten_xxx` IDs but JWT
carried Clerk org IDs → FK violation would follow even if length was fixed.

**Fix:**

- Migrated all ID columns from `String(20)` → `String(50)`
- Removed `clerk_org_id` and `clerk_user_id` shadow columns
- Adopted Clerk IDs directly as DB primary identifiers
- Removed `generate_tenant_id()` and `generate_user_id()` from `ids.py`
- Alembic migration required DROP + recreate of all 4 RLS policies before
  ALTER COLUMN (PostgreSQL blocks ALTER on policy-referenced columns)
- Updated `conftest.py` and `seed.py` to use Clerk-style test IDs

**Decisions made:**

- Clerk IDs as DB identifiers — one less ID to manage, no mapping layer
- String(50) — headroom for Clerk's current 31-char IDs + future growth

---

#### Fix: Clerk JWT verification — added JWT_KEY and authorized_parties

**Problem:** `verify_token()` was not using `jwt_key` for offline
verification or restricting `authorized_parties`.

**Fix:**

- Added `jwt_key: str` to `_ClerkSettings`
- Added `authorized_parties=["http://localhost:3000"]` and
  `jwt_key=_settings.jwt_key` to `AuthenticateRequestOptions`
- Added `JWT_KEY` (PEM public key) to `.env`
- Removed duplicate `model_config` (inherits from `BaseServiceSettings`)

**Decisions made:**

- `JWT_KEY` enables offline JWT verification — no network call to Clerk
  on every request, faster and more resilient
- `authorized_parties` restricts which frontend domains can authenticate —
  prevents token reuse from other apps

---

#### Fix: docker-compose.yml healthcheck URL

- api-gateway healthcheck was hitting `/health` — fixed to `/api/v1/health`

---

#### Feature: organizationMembership.created webhook handler

**Problem:** `user.created` fires before the user joins any org —
`organization_memberships` is always empty. Users were never getting
inserted into the DB, causing FK violation on Step 2 of onboarding.

**Fix:** Added `handle_membership_created()` handler:

- Subscribed to `organizationMembership.created` in Clerk dashboard
- Extracts `organization.id`, `public_user_data.user_id`,
  `public_user_data.identifier` (email)
- Maps `org:admin` → `UserRole.ADMIN`, anything else → `UserRole.MEMBER`
- Guards: empty org_id, empty user_id, missing keys → early return
- Duplicate guard — silent skip if user already exists

**Decisions made:**

- `organizationMembership.created` is the correct event for user
  provisioning — both user and org info present in one payload
- `user.created` kept for compatibility but always returns early

---

#### Fix: user.created empty email_addresses IndexError

**Problem:** Clerk test payload sends `email_addresses: []` —
accessing `[][0]` crashed with `IndexError`.

**Fix:**

```python
email_addresses = data.get("email_addresses", [])
email = email_addresses[0].get("email_address", "") if email_addresses else ""

### Hotfix — Clerk Integration: Clerk IDs too long + auth gaps

**Date:** May 19, 2026
**Relates to:** COM-19, COM-18

**What was done:**

- **VARCHAR(20) → VARCHAR(50)** — Clerk org IDs are 31 chars; all `tenant_id`,
  `user_id`, `changed_by` columns widened
- **Dropped clerk_org_id / clerk_user_id shadow columns** — Clerk IDs now used
  directly as DB primary identifiers; no mapping layer needed
- **Alembic migration** — required DROP + recreate of all 4 RLS policies before
  ALTER COLUMN (PostgreSQL blocks ALTER on policy-referenced columns)
- **JWT_KEY added** — PEM public key from Clerk dashboard added to `.env`;
  enables offline JWT verification without network call to Clerk
- **authorized_parties** — restricted to `["http://localhost:3000"]` in
  `AuthenticateRequestOptions`; prevents token reuse from other apps
- **Fixed docker-compose.yml** — api-gateway healthcheck was hitting `/health`;
  corrected to `/api/v1/health`
- **Fixed user.created empty email_addresses** — `[][0]` crashed with `IndexError`;
  fixed with `if email_addresses else ""`
- Updated `conftest.py` and `seed.py` — replaced `generate_tenant_id()` with
  Clerk-style test IDs (`org_test_xxx`)

**Decisions made:**

- Clerk IDs as DB identifiers — one less ID to manage, no mapping layer
- `String(50)` — headroom for Clerk's current 31-char IDs + future growth
- Offline JWT verification — faster, no Clerk API dependency on every request

**Blockers hit + fixes:**

- `FeatureNotSupportedError` — PostgreSQL blocks ALTER COLUMN TYPE when RLS
  policy references the column; fixed by DROP policy → ALTER → recreate policy
  in migration

---

### Hotfix — Clerk Integration: organizationMembership.created webhook

**Date:** May 19, 2026
**Relates to:** COM-19

**What was done:**

- Added `handle_membership_created()` to `webhooks.py`
- Subscribed to `organizationMembership.created` in Clerk dashboard
- Handler extracts `organization.id`, `public_user_data.user_id`,
  `public_user_data.identifier` (email) from payload
- Maps `org:admin` → `UserRole.ADMIN`, anything else → `UserRole.MEMBER`
- Guards against empty org_id, empty user_id, missing keys → early return
- Duplicate guard — silent skip if user already exists
- Tested via Clerk dashboard Testing tab → user row inserted correctly

**Root cause:** `user.created` fires before user joins any org —
`organization_memberships` is always empty at that point.
`organizationMembership.created` is the correct event — both user and org
info present in one payload.

**Blockers: None**

---

### COM-136 — Onboarding Step 1: Company profile form ✅
### COM-137 — Onboarding Step 2: Tech stack selector ✅
### COM-138 — Onboarding Step 3: Data categories selector ✅
### COM-139 — Onboarding Step 4: Countries of operation ✅
### COM-140 — Onboarding Step 5: Team setup and final submission ✅

**Date:** May 19–20, 2026
**Status:** Done

**What was done:**

- Tested all 5 onboarding steps end-to-end with real Clerk JWT auth
- All steps call PATCH `/api/v1/profile` and persist correctly to PostgreSQL
- Data persistence confirmed — refresh at each step shows previously saved data
- `is_complete = true` correctly set after Step 5
- Webhook flow confirmed — `organization.created` → tenant row,
  `organizationMembership.created` → user row, onboarding proceeds without errors

**Blockers hit + fixes:**

- `StringDataRightTruncationError` — Clerk org ID (31 chars) exceeded VARCHAR(20);
  fixed in Clerk Integration Hotfix above
- `ForeignKeyViolationError` on Step 2 — `company_profile_versions.changed_by` FK
  references `users` table; user row missing because webhook wasn't set up when
  account was created; fixed by adding `organizationMembership.created` handler
- Manual DB inserts required for dev account (tenant + user) — only needed
  for accounts created before webhooks were configured; new signups fully automatic

```

---

## 2026-05-21 — COM-145: Switch api-gateway to app_user DB connection

**Branch:** `feat/COM-145-rls-app-user`
**Status:** Done

### What was done

- Created `app_user_engine` and `AppUserSessionLocal` in `common/db/session.py` — all authenticated requests now run as `app_user` (non-superuser), making RLS policies active at runtime
- Kept `admin_engine` / `AdminSessionLocal` for webhook endpoints — superuser needed there to bypass RLS for user provisioning
- Updated `common/db/tenant.py` — `get_tenant_session()` now uses `AppUserSessionLocal`
- Updated `common/db/__init__.py` and `services/api-gateway/app/main.py` — renamed `engine` → `admin_engine`
- Added `app_user_database_url` field to `BaseServiceSettings` with Railway URL fix validator
- Added `APP_USER_DATABASE_URL` to `.env`, `.env.example`, and CI env block
- Alembic migration `f2fc0fffc4df` — backfilled permissions on tables created after original `app_user` grant, added `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` so all future tables are auto-granted to `app_user` without any manual intervention
- Fixed `alembic.ini` — removed hardcoded `sqlalchemy.url = localhost` that was overriding env var inside Docker
- Fixed `Makefile` migrate command — added absolute path `-c /app/packages/common/alembic.ini`
- Updated `test_tenant_middleware.py` — patched `AppUserSessionLocal` instead of old `AsyncSessionLocal`

### Key decisions

- Two engines, not one — `admin_engine` (superuser, bypasses RLS) for webhooks only; `app_user_engine` (RLS enforced) for all API requests
- `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` — long-term fix so no migration author ever needs to manually grant permissions on new tables again
- CI uses postgres superuser for both URLs — CI runs tests, not RLS enforcement; real isolation tested in `test_rls_company_profile.py`

### Blockers hit + fixes

- `ImportError: cannot import name 'engine'` — `common/db/__init__.py` and `main.py` still imported old `engine` name; updated to `admin_engine`
- `alembic.ini` hardcoded `sqlalchemy.url = localhost` overriding container env var — commented out
- Makefile `make migrate` missing `-c` flag — alembic couldn't find `script_location`
- Docker containers started via Docker Desktop not recognised by `docker compose` — must always use `make up/down`, not Docker Desktop play button
- Tenant + user missing from DB after container recreation — manually inserted via `make db`; permanent fix is Clerk webhooks for new signups

**Test results:** 64 passed (31 api-gateway + 33 common)

**Blockers: None**

---

## 2026-05-22 — COM-141: Onboarding Wizard Polish

**Branch:** `feat/COM-141-onboarding-polish`
**Status:** Done

### What was done

- **Brand colors** — Added Navy (`#1E3A5F`) and Amber (`#F59E0B`) to Tailwind v4 `@theme` block in `globals.css`; applied across all UI components (`Button`, `SelectCard`, `CheckboxCard`, `Input`, `Tooltip`)
- **Sidebar step navigator** — New `StepSidebar` client component with logo, step list (completed = amber ✓, active = white, future = faded), and clickable completed steps via `<Link>`
- **Two-column onboarding layout** — `(onboarding)/layout.tsx` rewritten as `h-screen flex` shell with sidebar + scrollable content area; form card centered with `max-w-4xl mx-auto`
- **Progress bar + step header** — `[step]/page.tsx` redesigned with 5-segment amber progress bar and "Step X of 5" label
- **Zod validation on all 5 forms** — All required fields validated with `{ shouldValidate: true }` on `setValue` calls so errors clear immediately on selection; Zod v4 `error` (not `required_error`) used for booleans; `superRefine` for conditional DPO fields
- **`OtherInput` reusable component** — Chip-based custom input (draft → confirm on Enter/blur/Add click) used for "Other" across Step 1 (industry), Step 2 (data categories, subject categories, processing purposes), Step 4 (cloud providers), Step 5 (certifications)
- **Back button auto-save** — All Back buttons now PATCH current form state before navigating; uses `watch()` to capture partial data silently (no validation block)
- **Cross-step validation** — Step 5 final submit calls `getFirstIncompleteStep()` from `lib/validateOnboarding.ts`; redirects to first incomplete step with error message if any required fields are missing
- **Sign-in / sign-up redesign** — `(auth)/layout.tsx` rewritten as split-panel: Navy brand panel (left, hidden on mobile) + Clerk form on warm white (right)

### Key decisions

- `const renderXxx = ()` pattern throughout all forms — avoids React remounting inner components on every render (single-keystroke focus loss bug)
- Dedicated `toggleCategory / toggleSubject / togglePurpose` handlers in Step 2 — "Other" clearing logic inside the handler, not inline in JSX `onChange` props (consistent with Step 4's `toggleProvider`)
- Back button uses `watch()` not `handleSubmit` — users should never be blocked from navigating back by validation errors
- `getFirstIncompleteStep` in a dedicated `lib/validateOnboarding.ts` — reusable, testable, not buried in Step 5 JSX

### Files changed

- `frontend/src/app/globals.css`
- `frontend/src/app/(auth)/layout.tsx`
- `frontend/src/app/(onboarding)/layout.tsx`
- `frontend/src/app/(onboarding)/onboarding/step/[step]/page.tsx`
- `frontend/src/app/(onboarding)/_components/Step1Form.tsx` – `Step5Form.tsx`
- `frontend/src/app/(onboarding)/_components/StepSidebar.tsx` _(new)_
- `frontend/src/components/ui/Button.tsx`, `CheckboxCard.tsx`, `Input.tsx`, `SelectCard.tsx`, `Tooltip.tsx`
- `frontend/src/components/ui/OtherInput.tsx` _(new)_
- `frontend/src/lib/validateOnboarding.ts` _(new)_

### Blockers hit + fixes

- **React remounting / single-keystroke focus loss** — inner components defined as `const Comp = () =>` inside parent caused React to see a new component type on every render and remount; fixed by converting all to `const renderXxx = ()` and calling as `{renderXxx()}`
- **Zod v4 `required_error` doesn't exist** — Zod v4 changed the API; `z.boolean({ required_error: "..." })` → `z.boolean({ error: "..." })`
- **Typed routes error on `<Link href>`** — Next.js typed routes rejects template literal strings; fixed with `as any` cast (consistent with all other `router.push` calls in the codebase)

**Blockers: None**

## COM-157 — Rulebook Tables + pgvector

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Switched PostgreSQL Docker image from `postgres:16` to `pgvector/pgvector:pg16`
- Added `pgvector>=0.3.0` and `openai>=1.30.0` to `packages/common/pyproject.toml`
- Created 4 new SQLAlchemy models: `Regulation`, `RegulationVersion`, `Rule`, `RuleVersion`
- Added nanoid-based public ID generators: `reg_`, `rgv_`, `rul_`, `rlv_`
- Created Alembic migration `9c6a4fe3c1ce`:
  - 5 PostgreSQL native enums
  - 4 tables with proper FK constraints
  - IVFFlat vector index on `rules.embedding` (cosine similarity, lists=100)

### Key Decisions

- **IVFFlat with lists=100** — optimal for 10k–100k vectors, fast cosine similarity for RAG
- **`use_alter=True`** for circular FK between `rules` and `rule_versions` — standard SQLAlchemy pattern
- **Separate public IDs** (`rul_xxx`) from internal UUIDs — external-facing IDs never expose DB internals

### What We Learned

- pgvector requires `pgvector/pgvector:pg16` Docker image — plain `postgres:16` doesn't have the extension
- Circular FK in Alembic migrations must be handled by creating tables first without the FK, then adding it via `ALTER TABLE` in the same migration
- After adding a migration file locally, `make rebuild-api` is needed before `make migrate` so the container picks up the new file

### Files Changed

- `infrastructure/docker/docker-compose.yml`
- `packages/common/pyproject.toml`
- `packages/common/common/utils/ids.py`
- `packages/common/common/models/regulation.py` ← new
- `packages/common/common/models/rule.py` ← new
- `packages/common/common/models/__init__.py`
- `packages/common/alembic/versions/9c6a4fe3c1ce_create_rulebook_tables.py` ← new

## COM-188 — Azure OpenAI Client Module

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Added `AIServiceSettings` class to `packages/common/common/config.py` extending `BaseServiceSettings`
- Created `packages/common/common/ai/client.py` with:
  - `get_async_client()` — returns `AsyncAzureOpenAI` singleton via `lru_cache(maxsize=1)`
  - `get_sync_client()` — returns `AzureOpenAI` singleton via `lru_cache(maxsize=1)`
- Created `packages/common/common/ai/__init__.py`
- Updated `services/policy-engine/app/config.py` to extend `AIServiceSettings` instead of `BaseServiceSettings`

### Key Decisions

- **Azure OpenAI over plain OpenAI** — EU data residency, DPA available, no data used for model training. Customer personal data never leaves the EU region
- **`lru_cache(maxsize=1)` singleton pattern** — one client instance per process, avoids connection pool exhaustion
- **`ai_enabled` property** — services can check `settings.ai_enabled` before making AI calls, gracefully degrading when keys aren't configured
- **`AIServiceSettings` as a mixin** — only services that need AI extend it, others use plain `BaseServiceSettings`

### Data Privacy Architecture

Only anonymised company characteristics go to Azure OpenAI — never:

- `dpo_name`, `dpo_email`, `legal_contact_email`
- `tenant_name`, `profile_id`
- Any personally identifiable information

### What We Learned

- Azure OpenAI uses the same `openai` Python package — just different client class (`AsyncAzureOpenAI`) and endpoint configuration
- Keys not needed at development time — `ai_enabled` returns `False` gracefully until Azure keys are configured

### Files Changed

- `packages/common/common/config.py`
- `packages/common/common/ai/__init__.py` ← new
- `packages/common/common/ai/client.py` ← new
- `services/policy-engine/app/config.py`

## COM-158 — Seed GDPR (99 Articles)

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Created `packages/common/common/utils/enums.py` with `pg_enum()` utility function
- Created `packages/common/scripts/seeders/seed_gdpr.py` seeding:
  - 1 regulation row (`GDPR`)
  - 1 regulation version row (`2016/679`)
  - 99 articles across all 11 GDPR chapters

### Articles Coverage

| Chapter | Articles  | Topic                              |
| ------- | --------- | ---------------------------------- |
| I       | 1–4       | General provisions & definitions   |
| II      | 5–11      | Core principles                    |
| III     | 12–23     | Data subject rights                |
| IV      | 24–43     | Controller & processor obligations |
| V       | 44–49, 50 | International transfers            |
| VI      | 51–59     | Supervisory authorities            |
| VII     | 60–76     | Cross-border cooperation           |
| VIII    | 77–84     | Fines & penalties                  |
| IX      | 85–91     | Special processing situations      |
| X       | 92–93     | Delegated acts                     |
| XI      | 94–99     | Final provisions                   |

### Key Decisions

- **`pg_enum()` utility** — wraps SQLAlchemy `Enum` with `values_callable` to always send `.value` (lowercase) not `.name` (uppercase) to PostgreSQL. One function used everywhere — impossible to forget
- **`str, enum.Enum` mixin** — kept on all enum classes for JSON/API serialization consistency
- **Idempotent seeder** — checks if GDPR already exists before inserting, safe to re-run anytime
- **`date()` objects not strings** — asyncpg requires Python `date` objects for `DATE` columns, not string literals

### Bugs Found & Fixed

- `asyncpg` sends enum `.name` (`"ACTIVE"`) not `.value` (`"active"`) by default — fixed with `pg_enum()` utility
- Date fields must be Python `date(2018, 5, 25)` not string `"2018-05-25"` — asyncpg strict about types
- Article 50 was initially missed — caught by article count check (98 vs 99), added and reseeded

### What We Learned

- SQLAlchemy native enum serialization with asyncpg uses `.name` by default — requires `values_callable` to use `.value`
- PostgreSQL convention: enum values lowercase, Python convention: enum names uppercase — `pg_enum()` bridges this gap permanently
- Always verify seeded count matches expected count before moving on

### Files Changed

- `packages/common/common/utils/enums.py` ← new
- `packages/common/scripts/__init__.py` ← new
- `packages/common/scripts/seeders/__init__.py` ← new
- `packages/common/scripts/seeders/seed_gdpr.py` ← new

## COM-159 — Seed NIS2 (46 Articles)

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Created `packages/common/scripts/seeders/seed_nis2.py` seeding:
  - 1 regulation row (`NIS2`)
  - 1 regulation version row (`2022/2555`)
  - 46 articles across all 8 NIS2 chapters

### Articles Coverage

| Chapter | Articles | Topic                                |
| ------- | -------- | ------------------------------------ |
| I       | 1–4      | General provisions & scope           |
| II      | 5–11     | Coordinated cybersecurity frameworks |
| III     | 12–25    | Risk management & incident reporting |
| IV      | 26–28    | Jurisdiction & registration          |
| V       | 29–30    | Information sharing                  |
| VI      | 31–38    | Supervisory & enforcement            |
| VII     | 39–40    | Delegated & implementing acts        |
| VIII    | 41–46    | Transitional & final provisions      |

### Key Decisions

- **Essential vs Important entity classification** — captured in `nis2_data.entity_type` from onboarding Step 6. Essential entities face proactive supervision; important entities reactive
- **Art. 21 (10 minimum measures)** — most critical article, `check_type=technical`, covers MFA, encryption, BCP, supply chain, incident response
- **Art. 23 (incident reporting)** — 3-stage timeline: 24h early warning → 72h notification → 1-month final report. `deadline_hours=24` in `evaluation_logic`
- **Art. 34 (fines)** — Essential: €10M/2% global turnover; Important: €7M/1.4% global turnover. Management personal liability included

### NIS2 vs GDPR Key Difference

NIS2 is a **Directive** (member states transpose into national law) not a **Regulation** (directly applicable). This means national implementations may vary — flagged in relevant articles.

### What We Learned

- NIS2 has 46 articles — significantly shorter than GDPR because it's a framework directive, not a directly applicable regulation
- No double fining with GDPR — if a cyber incident is also a GDPR breach, only the higher fine applies (Art. 35)
- Transposition deadline was 17 October 2024 — NIS2 is now fully in force across EU

### Files Changed

- `packages/common/scripts/seeders/seed_nis2.py` ← new

## COM-160 — Seed EU AI Act (113 Articles)

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Created `packages/common/scripts/seeders/seed_eu_ai_act.py` seeding:
  - 1 regulation row (`EU_AI_ACT`)
  - 1 regulation version row (`2024/1689`)
  - 113 articles across all 11 chapters
- Created `packages/common/scripts/seeders/seed_all.py` — runs all 3 seeders in order
- Added Makefile targets: `make seed`, `make seed-gdpr`, `make seed-nis2`, `make seed-euai`

### Articles Coverage

| Chapter | Articles | Topic                                                            |
| ------- | -------- | ---------------------------------------------------------------- |
| I       | 1–4      | General provisions, definitions, AI literacy                     |
| II      | 5        | Prohibited AI practices (8 categories)                           |
| III     | 6–49     | High-risk AI systems (classification, requirements, obligations) |
| IV      | 50       | Transparency obligations                                         |
| V       | 51–56    | General-purpose AI (GPAI) models                                 |
| VI      | 57–63    | Innovation measures & sandboxes                                  |
| VII     | 64–70    | Governance                                                       |
| VIII    | 71       | EU database for high-risk AI                                     |
| IX      | 72–87    | Post-market monitoring, enforcement, penalties                   |
| X       | 88–94    | Codes of conduct, AI Board, advisory forum                       |
| XI      | 95–113   | Final provisions, sector amendments, transitional                |

### Key Decisions

- **Risk-based approach** — 4 tiers: prohibited, high-risk, limited risk, minimal risk. Severity mapped accordingly
- **Art. 5 (prohibited practices)** — `severity=critical`, 8 banned AI types including social scoring, real-time biometric surveillance, emotion recognition in workplace. Applies from **2 February 2025**
- **Art. 21 (high-risk requirements)** — 10 minimum measures including risk management, data governance, human oversight, MFA, encryption
- **Art. 50 (transparency)** — chatbots must disclose they are AI, AI-generated content must be watermarked. Applies from **August 2026**
- **Art. 79 (fines)** — 3 tiers: €35M/7% for prohibited AI, €15M/3% for high-risk violations, €7.5M/1.5% for misleading authorities

### Phased Application Timeline

| Deadline        | What applies                                |
| --------------- | ------------------------------------------- |
| 2 February 2025 | Prohibited AI practices (Art. 5)            |
| 2 August 2025   | GPAI model obligations (Chapter V)          |
| 2 August 2026   | High-risk AI obligations (Chapters III, IV) |
| 2 August 2027   | Legacy AI systems must be compliant         |

### Provider vs Deployer

Critical distinction captured in `ai_act_data.role`:

- **Provider** — builds/sells AI. Responsible for conformity assessment, CE marking, technical docs, EU database registration
- **Deployer** — uses AI in products/services. Responsible for human oversight, logs, incident reporting, fundamental rights impact assessment

### What We Learned

- EU AI Act is the world's first comprehensive AI regulation — risk-based, not technology-specific
- GPAI systemic risk threshold: 10^25 FLOPs training compute — currently applies to frontier models like GPT-4 class systems
- Highest fine in any EU tech regulation: €35M or 7% global turnover for prohibited AI — higher than GDPR Tier 2

### Files Changed

- `packages/common/scripts/seeders/seed_eu_ai_act.py` ← new
- `packages/common/scripts/seeders/seed_all.py` ← new
- `Makefile`

## COM-161 — Regulations API Endpoints

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Created `services/policy-engine/app/routers/__init__.py`
- Created `services/policy-engine/app/routers/regulations.py` with 2 endpoints:
  - `GET /api/v1/regulations` — list all regulations
  - `GET /api/v1/regulations/{name}/rules` — get rules for a regulation with filters
- Updated `services/policy-engine/app/main.py` to include the router
- Created `services/policy-engine/tests/__init__.py`
- Created `services/policy-engine/tests/conftest.py`
- Created `services/policy-engine/tests/test_regulations.py` — 34 test cases

### Endpoints

**GET /api/v1/regulations**
Returns all regulations with name, full_name, jurisdiction, authority, status, effective_date, source_url.

**GET /api/v1/regulations/{name}/rules**

- Path param: regulation name (case insensitive — `gdpr`, `GDPR`, `Gdpr` all work)
- Query params: `?category=`, `?severity=`, `?check_type=` (all case insensitive)
- Returns: regulation name, total count, full rules array
- Filters: all values lowercased before querying — `?severity=CRITICAL` works same as `?severity=critical`

### Test Coverage (34 cases)

| Category                    | Count |
| --------------------------- | ----- |
| List regulations happy path | 4     |
| HTTP method enforcement     | 4     |
| Rules happy path            | 3     |
| Case insensitivity (name)   | 4     |
| Not found / edge cases      | 6     |
| Filter behaviour            | 8     |
| Inactive rules              | 1     |
| Empty results               | 1     |
| Health check unaffected     | 1     |
| Method not allowed          | 2     |

### Bugs Found & Fixed

- `HTTPException` imported inside function body — moved to top-level import
- Filter values were case-sensitive — `?severity=CRITICAL` returned empty list. Fixed by calling `.lower()` on all filter values before querying

### Key Decisions

- **No auth on regulations endpoints** — regulations are system-level reference data, not tenant data. No RLS needed, uses admin session
- **Case-insensitive name lookup** — `.upper()` on path param so `gdpr`/`GDPR`/`Gdpr` all resolve correctly
- **Case-insensitive filters** — `.lower()` on all query params before querying DB
- **404 vs empty list** — unknown regulation = 404; known regulation with no matching rules = 200 empty list
- **Unsupported filters silently ignored** — `?is_mandatory=true` ignored, returns all rules (by design)

### What We Learned

- SQL injection via SQLAlchemy ORM is architecturally impossible — parameterized queries always used. Test for endpoint behaviour (404), not library internals
- FastAPI returns 405 automatically for undefined HTTP methods — no extra code needed
- Empty string query params (`?severity=`) are falsy in Python — treated as no filter

### Files Changed

- `services/policy-engine/app/main.py`
- `services/policy-engine/app/routers/__init__.py` ← new
- `services/policy-engine/app/routers/regulations.py` ← new
- `services/policy-engine/tests/__init__.py` ← new
- `services/policy-engine/tests/conftest.py` ← new
- `services/policy-engine/tests/test_regulations.py` ← new

## BONUS — Step 6 Onboarding (GDPR / NIS2 / EU AI Act Data Collection)

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Created `frontend/src/app/(onboarding)/_components/Step6Form.tsx`
- Updated `frontend/src/app/(onboarding)/_components/StepSidebar.tsx` — added Step 6
- Updated `frontend/src/app/(onboarding)/onboarding/step/[step]/page.tsx` — `TOTAL_STEPS` 5→6, added Step6Form
- Updated `frontend/src/app/(onboarding)/_components/Step5Form.tsx` — removed `is_complete: true`, changed "Finish" to "Continue →"
- Updated `frontend/src/lib/validateOnboarding.ts` — added Step 6 validation

### Step 6 Sections

**GDPR Section**

- Lawful bases (multi-select: consent, contract, legal obligation, vital interests, public task, legitimate interests)
- Processes children's data (yes/no)
- Transfers outside EEA (yes/no)
- Transfer mechanisms (multi-select: SCCs, adequacy decision, BCRs, derogations)
- Uses data processors (yes/no)
- Has breach notification procedure (yes/no)
- Has DPIA process (yes/no)

**NIS2 Section** (conditional — only shown if NIS2 sectors selected)

- NIS2 sectors (multi-select: energy, transport, banking, health, digital infrastructure, etc.)
- Entity type (essential / important)
- Uses MFA (yes/no)
- Has incident response plan (yes/no)
- Has business continuity plan (yes/no)
- Supply chain security policy (yes/no)

**EU AI Act Section**

- Uses AI (yes/no)
- Role (provider / deployer / both)
- High-risk AI categories (multi-select: biometric, employment, education, law enforcement, etc.)
- Develops GPAI models (yes/no)
- Has AI governance policy (yes/no)

### Key Decisions

- **Saves to JSONB columns** — `gdpr_data`, `nis2_data`, `ai_act_data` on the profile
- **`is_complete: true` moved to Step 6** — onboarding only complete after all 6 steps
- **NIS2 section conditional** — only shown if organisation operates in NIS2-covered sectors
- **Step 6 is the final step** — submitting sets `is_complete: true` and redirects to dashboard

### Patterns Followed (matching Steps 1-5)

- `type FormData = z.infer<typeof schema>` — no renaming
- No `.default()` in Zod schema — uses `.optional()` with `defaultValues`
- `watch("field") ?? []` — for optional array fields
- `renderYesNo()` returns just buttons div — caller wraps in `FormField`
- Dedicated toggle handlers — no generic `toggleMulti`
- No `SubmitHandler` import

### What We Learned

- Never use `.default([])` in Zod schema with react-hook-form — causes Resolver type mismatch
- `SubmitHandler` generic type causes TypeScript errors — use `type FormData` pattern consistently
- Stick to established patterns across all step forms — deviating causes hard-to-debug TypeScript errors

### Files Changed

- `frontend/src/app/(onboarding)/_components/Step6Form.tsx` ← new
- `frontend/src/app/(onboarding)/_components/Step5Form.tsx`
- `frontend/src/app/(onboarding)/_components/StepSidebar.tsx`
- `frontend/src/app/(onboarding)/onboarding/step/[step]/page.tsx`
- `frontend/src/lib/validateOnboarding.ts`

## BONUS — Schema Improvements (fine_tier, is_mandatory, check_type)

**Date:** 2026-05-30
**Branch:** feat/sprint-2-phase-1-rulebook-foundation

### What was built

- Added 3 new columns to `rules` table:
  - `fine_tier` — `VARCHAR(10)`, nullable, indexed (`"tier_1"`, `"tier_2"`, `None`)
  - `is_mandatory` — `BOOLEAN`, not null, default `true`
  - `check_type` — `VARCHAR(30)`, not null, default `"informational"`, indexed
- Added 2 new columns to `rule_versions` table:
  - `fine_tier` — nullable (historical snapshots may not have it)
  - `is_mandatory` — nullable (same reason)
- Migration `0cdd1cbf1525` — adds all 5 columns, recreates all indexes correctly

### Why These Columns

| Column         | Why a column (not JSONB)                                                          |
| -------------- | --------------------------------------------------------------------------------- |
| `fine_tier`    | Queried directly for risk scoring: `WHERE fine_tier = 'tier_2'`                   |
| `is_mandatory` | Filtered for mandatory vs optional rules: `WHERE is_mandatory = true`             |
| `check_type`   | Assessment engine picks evaluation strategy: `WHERE check_type = 'profile_field'` |

### check_type Values

| Value               | Meaning                                |
| ------------------- | -------------------------------------- |
| `profile_field`     | Evaluated from onboarding profile data |
| `document_required` | Needs a document uploaded              |
| `policy_required`   | Needs a written policy                 |
| `technical`         | Needs a technical control verified     |
| `informational`     | Awareness only, no active check        |

### Migration Fix Applied

Autogenerated migration dropped `rules_embedding_idx` (IVFFlat) and `rules_tags_idx` (GIN) without recreating them. Manually added back:

```python
op.create_index('ix_rules_embedding', 'rules', ['embedding'],
    postgresql_using='ivfflat',
    postgresql_ops={'embedding': 'vector_cosine_ops'},
    postgresql_with={'lists': '100'})
op.create_index('ix_rules_applicability_tags', 'rules',
    ['applicability_tags'], postgresql_using='gin')



```

## COM-162 — Migrate Assessments and Gaps Tables + RLS

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- Created `Assessment` SQLAlchemy model (`packages/common/common/models/assessment.py`)
- Created `Gap` SQLAlchemy model in same file
- Added `generate_assessment_id()` → `asm_xxx` and `generate_gap_id()` → `gap_xxx` to `ids.py`
- Alembic migration `12cd2212cee0` creating both tables with RLS

### Assessment table

Stores one row per compliance assessment run per tenant per regulation:

- Score (0-100), risk_level, met/partial/not_met/unknown counts
- `profile_snapshot` (JSONB) — profile state at time of assessment (critical for audit trail)
- `previous_assessment_id` — FK to prior assessment for score delta tracking
- `regulation_version_id` — which version of the regulation was assessed
- `expires_at` — when to re-assess (drives upcoming deadlines widget)
- RLS on `tenant_id`

### Gap table

Stores one row per rule per assessment:

- Denormalized fields from rule (`severity`, `category`, `article`, `article_number`, `chapter`, `fine_tier`, `regulation_name`) — avoids joins for display performance
- `status` — met | partial | not_met | unknown | not_applicable
- `evidence` (JSONB) — what profile data triggered this evaluation
- `profile_field_value` (JSONB) — exact value used for audit trail
- `remediation_steps`, `remediation_resources` (JSONB) — personalised guidance
- `assigned_to`, `due_date` — task assignment for remediation roadmap
- `resolved`, `resolved_at`, `resolved_by` — resolution tracking
- RLS on `tenant_id`

### Key Decisions

- **Denormalized display fields on gaps** — severity, category, article etc. copied from rule at assessment time. Avoids joins in every dashboard query. Trade-off: takes more storage, but gap list queries are 10x faster
- **profile_snapshot on assessments** — when profile changes, historical scores remain accurate. Without this, you can't explain why score was 34% last month
- **`not_applicable` as a gap status** — we store all 258 rules as gaps, including non-applicable ones. Makes it easy to show "why this rule doesn't apply to you"

### What We Learned

- Alembic autogenerate drops IVFFlat and GIN indexes every time — always manually remove those drop statements before running migration
- RLS must be added manually to migration — Alembic never generates it

### Files Changed

- `packages/common/common/models/assessment.py` ← new
- `packages/common/common/utils/ids.py`
- `packages/common/common/models/__init__.py`
- `packages/common/alembic/versions/12cd2212cee0_add_assessments_and_gaps_tables.py` ← new

## COM-163 — Applicability Engine

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- Created `services/policy-engine/app/engine/applicability.py`
- `ApplicabilityEngine` class that takes a profile + rules + regulation name
- Returns `ApplicabilityResult` for each rule: `is_applicable` (bool) + `reason` (string for audit trail)

### How it works

1. Universal filters applied first (applies to all 258 rules)
2. Routes to regulation-specific logic (GDPR/NIS2/EU AI Act)
3. Returns list of results — scorer only evaluates applicable rules

### Universal filters

- `check_type = 'informational'` → always `not_applicable` (165 rules — awareness only)
- B2B/B2C mismatch → `not_applicable`

### GDPR applicability logic

| Condition                         | Articles affected                                |
| --------------------------------- | ------------------------------------------------ |
| `gdpr_data` empty/null            | All GDPR rules → not applicable                  |
| `data_role = processor`           | Arts. 13-26 (controller duties) → not applicable |
| `consent` not in lawful_bases     | Art. 7 → not applicable                          |
| `processes_children_data = false` | Art. 8 → not applicable                          |
| No special category data          | Art. 9 → not applicable                          |
| No criminal conviction data       | Art. 10 → not applicable                         |
| No consent/contract basis         | Art. 20 → not applicable                         |
| `uses_ai = false`                 | Art. 22 → not applicable                         |
| `uses_data_processors = false`    | Arts. 19, 28, 29 → not applicable                |
| `transfers_outside_eea = false`   | Arts. 44-49 → not applicable                     |
| EU jurisdiction                   | Art. 27 → not applicable                         |

### NIS2 applicability logic

| Condition                           | Effect                                         |
| ----------------------------------- | ---------------------------------------------- |
| `nis2_data` empty/null              | All NIS2 → not applicable                      |
| `nis2_sectors` empty                | All NIS2 → not applicable                      |
| `company_size` in {"1-10", "11-50"} | All NIS2 → not applicable (micro/small exempt) |
| `entity_type != "essential"`        | Art. 32 → not applicable                       |
| `entity_type != "important"`        | Art. 33 → not applicable                       |
| Not DNS/TLD sector                  | Art. 28 → not applicable                       |

### EU AI Act applicability logic

| Condition                | Effect                                            |
| ------------------------ | ------------------------------------------------- |
| `ai_act_data` empty/null | All AI Act → not applicable                       |
| `uses_ai = false`        | All AI Act → not applicable                       |
| No high-risk categories  | Arts. 8-49 (except 6,7) → not applicable          |
| `role` not provider/both | Arts. 16-25 provider obligations → not applicable |
| `role` not deployer/both | Arts. 26-27 deployer obligations → not applicable |
| `gpai_model = false`     | Arts. 51-56 → not applicable                      |
| EU jurisdiction          | Art. 22 (EU representative) → not applicable      |

### Key Decisions

- **`reason` field on every result** — full audit trail of why a rule was or wasn't applied. Essential for compliance audits — customers can ask "why doesn't Art. 44 apply to me?"
- **`role = "both"` applies everything** — companies that are both provider and deployer get all obligations
- **Informational filtered first** — before regulation-specific logic, saves processing
- **NIS2 size threshold enforced** — micro/small companies (< 50 employees) are legally exempt from NIS2; we respect this

### What We Learned

- GDPR Art. 27 (EU representative) uses substring matching on jurisdiction — "Ireland" contains "ireland" which is in EU_JURISDICTIONS set. Handles all EU member states correctly
- `data_role = "both"` edge case — must NOT skip any obligations, only `processor` alone skips controller duties

### Files Changed

- `services/policy-engine/app/engine/__init__.py` ← new
- `services/policy-engine/app/engine/applicability.py` ← new

## COM-164 — Per-Article Scoring Logic

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- Created `services/policy-engine/app/engine/scorer.py`
- `Scorer` class that takes profile + applicability results
- Returns `ScoringResult` per applicable rule: status, score, evidence, remediation_priority
- `calculate_overall_score()` — weighted score (0-100) + risk level + counts

### Scoring statuses

| Status    | Score | Meaning                                |
| --------- | ----- | -------------------------------------- |
| `met`     | 100   | Company satisfies this requirement     |
| `partial` | 50    | Partially satisfies — some gaps remain |
| `not_met` | 0     | Clearly does not satisfy               |
| `unknown` | 0     | Not enough profile data to evaluate    |

### Severity weights

| Severity | Weight |
| -------- | ------ |
| critical | 4      |
| high     | 3      |
| medium   | 2      |
| low      | 1      |

### Score formula

- earned = sum(weight × score_multiplier) for each non-unknown rule
- total = sum(weight) for each non-unknown rule
- score = round(earned / total × 100)

### Risk levels

| Score | Risk level |
| ----- | ---------- |
| >= 80 | low        |
| >= 60 | medium     |
| >= 40 | high       |
| < 40  | critical   |

### What gets scored (Level 1 — profile_field rules only)

| Rule            | Met when                              | Not met when                 | Unknown when                        |
| --------------- | ------------------------------------- | ---------------------------- | ----------------------------------- |
| Art. 6          | lawful_bases not empty                | lawful_bases empty           | —                                   |
| Art. 33/34      | has_breach_procedure = true           | has_breach_procedure = false | has_breach_procedure = null         |
| Art. 35/36      | has_dpia = true                       | has_dpia = false             | has_dpia = null                     |
| Art. 37/38/39   | has_compliance_officer + name + email | —                            | no DPO or missing details → partial |
| Arts. 44-49     | transfers + mechanisms                | transfers + no mechanisms    | —                                   |
| NIS2 Art. 18/23 | has_incident_plan = true              | has_incident_plan = false    | has_incident_plan = null            |

### What stays unknown (Levels 2-4 — future)

- `policy_required` (32 rules) — need yes/no checklist
- `document_required` (21 rules) — need document upload
- `technical` (15 rules) — need technical verification

Unknown rules are shown as gaps but excluded from score denominator — they don't penalise the score, they show what's left to evaluate.

### Key Decisions

- **Unknown excluded from score denominator** — if a company has 10 evaluable rules (all met) + 50 unknown rules, their score is 100/100 not 10/60. Unknown = "we don't know yet", not "you failed". This prevents penalising companies for incomplete data
- **Partial for DPO with missing details** — `has_compliance_officer = true` but missing name/email → partial (50). They have a DPO, but documentation is incomplete
- **Evidence on every result** — every ScoringResult records what profile data was used. Critical for audit trail and explaining score to customers
- **`_result()` helper** — all scoring paths go through one helper to ensure consistent evidence recording and priority assignment

### What We Learned

- DPO scoring has 3 states: met (officer + name + email), partial (officer but missing details), unknown (no officer — might still be mandatory depending on processing)
- Transfer rules have an interesting met case: when `transfers_outside_eea = false`, the rule is technically met (no transfers = compliant). Applicability engine handles the "not applicable" case separately

### Files Changed

- `services/policy-engine/app/engine/scorer.py` ← new

## COM-165 — Remediation Generator

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- Created `services/policy-engine/app/engine/remediation.py`
- `RemediationGenerator` class — converts scoring results to prioritised action items
- `summary()` — aggregated counts by priority and status for dashboard

### Priority ordering

- `not_met + critical` → fix immediately
- `not_met + high` → fix urgently
- `unknown + critical` → gather data urgently
- `unknown + high` → gather data
- `partial + critical/high` → improve existing controls
- `not_met + medium` → fix when possible
- `unknown + medium/low` → lower priority data gathering
- `partial + medium/low` → improve when possible

### Fine exposure shown to users

- `tier_2` → "Up to €20M or 4% of global annual turnover"
- `tier_1` → "Up to €10M or 2% of global annual turnover"
- No tier → None

### Evidence needed messages (unknown rules only)

- `policy_required` → "Please confirm whether this policy exists"
- `document_required` → "Please upload or confirm the required document"
- `technical` → "Please confirm whether this technical control is implemented"

### Remediation steps fallback chain

- Use seeded `remediation_steps` from rule if available
- Fall back to `remediation_hint` as single step if steps empty
- Empty list if neither exists

### Key Decisions

- **Met rules excluded** — no action needed, keeps list focused
- **not_met ranked above unknown at same severity** — we know not_met is a problem; unknown might not be
- **Fine exposure on every item** — showing "€20M or 4% global turnover" next to a critical gap motivates action
- **`immediate_action_required` flag** — tells dashboard to show urgent banner when critical items exist

### Files Changed

- `services/policy-engine/app/engine/remediation.py` ← new

---

## COM-166 — Assessments API

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- Created `services/policy-engine/app/routers/assessments.py`
- 4 endpoints on policy-engine service

### Endpoints

- `POST /api/v1/assessments` — triggers assessment, returns 202 immediately with `assessment_id`
- `GET /api/v1/assessments/latest` — latest completed assessment per regulation for the tenant
- `GET /api/v1/assessments/{id}` — status + score for a specific assessment
- `GET /api/v1/assessments/{id}/gaps` — filterable gap list

### Gap list filters

- `?status=` — met | partial | not_met | unknown
- `?severity=` — critical | high | medium | low
- `?category=` — Security | Core Principles | etc.
- `?remediation_priority=` — critical | high | medium | low
- `?resolved=` — true | false
- `?limit=` + `?offset=` — pagination (max 500)

### Assessment flow

- Validates profile is complete before running
- Snapshots profile at assessment time → saved to `profile_snapshot`
- Finds previous completed assessment → sets `previous_assessment_id`
- Creates assessment row (status=pending)
- Queues ARQ job via Redis
- Returns 202 immediately — client polls GET for status

### Key Decisions

- **202 not 200** — assessment is async. Returning 200 would imply it's done
- **`not_applicable` gaps excluded from gap list** — not actionable. Dashboard only shows gaps the company can act on
- **Profile completeness check** — prevents running assessment before onboarding is done
- **Latest endpoint returns all 3 regulations** — dashboard can show all regulation scores in one request

### Files Changed

- `services/policy-engine/app/routers/assessments.py` ← new
- `services/policy-engine/app/main.py`

---

## COM-70 — Comprehensive Tests + ARQ Worker Architecture

**Date:** 2026-06-02
**Branch:** feat/sprint-2-phase-2-assessment-engine

### What was built

- 134 test cases in `services/policy-engine/tests/test_engine.py`
- ARQ worker in `services/policy-engine/app/workers/assessment.py`
- Separate `policy-engine-worker` Docker container

### Test coverage

- Applicability engine — all GDPR, NIS2, EU AI Act rules and edge cases
- Scorer — all profile_field rules, score calculations, boundary values
- Remediation generator — priority ordering, fine exposure, evidence needed
- Edge cases: None values, empty data, role combinations, boundary scores (40/60/80)

### ARQ Worker architecture

- `WorkerSettings` class with `redis_settings` parsed from `REDIS_URL`
- Warms rule cache on startup — all 258 rules loaded once per worker process
- Assessment pipeline:
  - Load assessment row from DB (1 query)
  - Load rules from cache (0 queries after warmup)
  - Run applicability engine (pure Python, ~1ms)
  - Run scorer (pure Python, ~1ms)
  - Run remediation generator (pure Python, ~1ms)
  - Bulk insert all gaps (1 query)
  - Update assessment status + score (1 query)
  - Total: 4 DB queries per assessment
- Separate Docker container with `MODE=worker` env var
- `restart: unless-stopped` — auto-recovers from crashes

### Key Decisions

- **4 DB calls not 258** — load rules once, evaluate in Python, bulk insert. Standard rule engine pattern
- **In-memory rule cache** — rules almost never change. Loading 258 rows on every assessment is wasteful. Cache warmed on startup, cleared on shutdown
- **ARQ over FastAPI BackgroundTasks** — BackgroundTasks are lost on server restart. ARQ persists jobs in Redis — survives deploys, crashes, OOM kills
- **Separate worker container** — API and worker can scale independently. Worker crash doesn't take down API. Clear separation of concerns

### What We Learned

- ARQ `WorkerSettings` must explicitly declare `redis_settings` — without it, ARQ defaults to `localhost:6379` regardless of env vars
- `.env` Redis URL should use Docker service name (`compliancekit-redis`) not `localhost` — all services run in Docker
- Rule cache `ROLLBACK` in logs is normal — SQLAlchemy opens a transaction on startup query even for SELECT, rolls back cleanly

### Files Changed

- `services/policy-engine/app/workers/__init__.py` ← new
- `services/policy-engine/app/workers/assessment.py` ← new
- `services/policy-engine/tests/test_engine.py` ← new
- `services/policy-engine/Dockerfile`
- `infrastructure/docker/docker-compose.yml`
- `.env`
- `services/policy-engine/pyproject.toml`

## Phase 3 — Compliance Dashboard

**Date:** 2026-06-03
**Branch:** feat/sprint-2-phase-3-dashboard

---

## COM-167/72 — Dashboard Shell (Portal Layout + Sidebar + TopBar)

### What was built

- Updated `frontend/src/app/(portal)/layout.tsx` — added Sidebar + main content wrapper
- Created `Sidebar.tsx` — navy sidebar matching onboarding design, nav items with "Soon" badges, sign out button, "← Back to Dashboard" link
- Created `TopBar.tsx` — server component showing page title + user info
- Updated `frontend/src/app/layout.tsx` — added `QueryProvider` (TanStack Query) + `ToastProvider` (Sonner)
- Created `frontend/src/components/providers/QueryProvider.tsx` — TanStack Query client with retry, staleTime, refetchOnWindowFocus

### Key Decisions

- **TanStack Query over SWR** — 52M vs 11M weekly downloads, first-class mutations with optimistic updates, rollback, DevTools. Industry standard for compliance SaaS with polling + mutations
- **Portal sidebar fixed position** — matches onboarding navy/amber design system
- **`md:ml-64 lg:ml-72`** — main content offset matches sidebar width responsively

### Files Changed

- `frontend/src/app/(portal)/layout.tsx`
- `frontend/src/app/(portal)/_components/Sidebar.tsx` ← new
- `frontend/src/app/(portal)/_components/TopBar.tsx` ← new
- `frontend/src/app/layout.tsx`
- `frontend/src/components/providers/QueryProvider.tsx` ← new
- `frontend/src/components/ui/Toast.tsx` ← new
- `frontend/src/components/ui/Modal.tsx` ← new
- `frontend/src/components/ui/Skeleton.tsx` ← new

---

## COM-168/73/74 — Compliance Score Widget + Regulation Cards

### What was built

- Created `ScoreGauge.tsx` — animated SVG circular gauge, animates counter from 0 to score on mount, colour-coded by risk level (green/amber/orange/red)
- Created `RegulationCard.tsx` — 6 states: never_run, pending/running (with spinner + timeout messages), completed (with gauge), failed (with retry), not_applicable
- Created `AssessmentSection.tsx` — orchestrates all 3 regulation cards, auto-triggers assessments on first visit, invalidates TanStack Query cache on trigger

### Key Decisions

- **Auto-trigger on first visit** — when `hasNeverRunAssessment` is true, immediately triggers all applicable regulations in parallel
- **Applicable regulations** — GDPR always; NIS2 only if `nis2_sectors` not empty; EU AI Act only if `uses_ai = true`
- **Polling every 3s** — `useAssessmentPolling` hook inside `RegulationCard` polls the specific assessment until completed or failed
- **Timeout messages** — 60s "Taking longer than expected", 5min "Something went wrong" — app never breaks silently
- **`latest` endpoint returns ALL statuses** — fixed to return pending/running assessments too (not just completed), so polling can start immediately

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/ScoreGauge.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/RegulationCard.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/AssessmentSection.tsx` ← new
- `services/policy-engine/app/routers/assessments.py` — fixed `latest` endpoint status filter

---

## COM-169/75 — Gap List + Article Detail Modal + Gap Resolve

### What was built

- Created `GapList.tsx` — search + 4 filters (severity, status, priority, resolved toggle), pagination (20 per page), empty states, error state with retry
- Created `GapItem.tsx` — gap row with severity dot, article name, category, fine exposure badge, status badge, chevron
- Created `GapDetailModal.tsx` — article title, severity/status/chapter badges, fine exposure warning, remediation steps numbered list, evidence used, notes textarea, resolve button
- Created `GapResolveButton.tsx` — resolve/unresolve with optimistic update + rollback on failure, resolved banner with date

### Key Decisions

- **Optimistic updates** — gap resolves instantly in UI, reverts if API fails. Uses TanStack Query `onMutate`/`onError` pattern
- **Pagination not infinite scroll** — compliance workflows need methodical review, not infinite scrolling
- **Client-side search** — search by article/category filters the current page without extra API call
- **`not_applicable` gaps excluded** — these aren't actionable, excluded from the gap list by default

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/GapList.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/GapItem.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/GapDetailModal.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/GapResolveButton.tsx` ← new

---

## COM-170 — Remediation Roadmap + Score History

### What was built

- Created `RemediationRoadmap.tsx` — gaps grouped by priority (critical/high/medium/low), each group shows gaps with status badges, clickable to open gap detail modal
- Created `ScoreTrendChart.tsx` — recharts line chart showing score over time, custom tooltip, empty state for first assessment, loading state

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/RemediationRoadmap.tsx` ← new
- `frontend/src/app/(portal)/dashboard/_components/ScoreTrendChart.tsx` ← new

---

## COM-76 — Upcoming Deadlines Widget

### What was built

- Created `DeadlinesWidget.tsx` — shows gaps with `due_date` set, sorted by date, urgency config (overdue/soon/upcoming) with colour coding, max 5 items

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/DeadlinesWidget.tsx` ← new

---

## COM-190 — Profile Completeness Widget

### What was built

- Created `ProfileCompletenessWidget.tsx` — checks all 6 onboarding sections, animated progress bar, "Complete →" links to incomplete steps, "Profile complete" celebration message at 100%

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/ProfileCompletenessWidget.tsx` ← new

---

## Bonus — Quick Wins Widget

### What was built

- Created `QuickWinsWidget.tsx` — shows top 5 low-effort gaps (medium/low severity, not_met), one-click resolve with optimistic update, score boost message

### Files Changed

- `frontend/src/app/(portal)/dashboard/_components/QuickWinsWidget.tsx` ← new

---

## Bonus — API Layer + TanStack Query Hooks

### What was built

- `frontend/src/lib/assessmentApi.ts` — all assessment API calls with typed error classes (NetworkError, AssessmentApiError), graceful fallbacks, no crashes on failure
- `frontend/src/lib/queryClient.ts` — TanStack Query client with retry=3, exponential backoff, refetchOnWindowFocus, refetchOnReconnect
- Hooks: `useLatestAssessments`, `useAssessment`, `useGaps`, `useUpdateGap` (optimistic), `useAssessmentHistory`, `useTriggerAssessment`, `useAssessmentStats`

### Files Changed

- `frontend/src/lib/assessmentApi.ts` ← new
- `frontend/src/lib/queryClient.ts` ← new
- `frontend/src/lib/hooks/` ← new (7 hooks)
- `frontend/src/types/assessment.ts` ← new

---

## Bonus — Backend Fixes

### JSON serialization fix

- **Problem**: `B2BOrB2C` enum not JSON serializable when storing `profile_snapshot` in JSONB
- **Fix**: Added custom `json_serializer` to SQLAlchemy engines in `session.py` — handles all enum types across the entire app. One change, fixes everything
- **Why not `str, enum.Enum`**: The serializer is cleaner — no need to change enum class definitions

### Gap fields migration

- Added `title`, `plain_english`, `remediation_hint` to `Gap` model — denormalized from Rule for display without joins
- Migration `cbbf5b013bae`
- ARQ worker now populates all 3 fields when creating gaps

### CORS fix

- Added `CORSMiddleware` to policy-engine `main.py`
- Frontend calls policy-engine directly via `NEXT_PUBLIC_POLICY_URL`

### What We Learned

- **TanStack Query `latest` endpoint bug**: Original endpoint only returned `COMPLETED` assessments — polling never started because `assessment_id` was always null. Fixed to return most recent assessment regardless of status
- **`json_serializer` on engine**: The right place to fix enum JSON serialization — one config, applies to all JSONB columns everywhere. Industry standard
- **`pg_enum()` vs `json_serializer`**: Two different problems. `pg_enum()` fixes PostgreSQL native enum column writes. `json_serializer` fixes JSONB column serialization. Both needed
- **CORS must be configured on the service receiving requests** — policy-engine needs its own CORS middleware since frontend calls it directly

### Files Changed

- `packages/common/common/db/session.py` — json_serializer
- `packages/common/common/models/company_profile.py` — enum cleanup
- `packages/common/alembic/versions/cbbf5b013bae_add_title_plain_english_remediation_.py` ← new
- `services/policy-engine/app/main.py` — CORS middleware
- `services/policy-engine/app/routers/assessments.py` — latest endpoint fix + gap resolve + history + stats endpoints
- `services/policy-engine/app/workers/assessment.py` — populate title/plain_english/remediation_hint
