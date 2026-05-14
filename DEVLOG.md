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
