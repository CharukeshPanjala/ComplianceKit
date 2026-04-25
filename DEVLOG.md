# ComplianceKit — Dev Log

Running diary of progress, decisions, and blockers across all sprints.
Updated every time a ticket is closed.

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
- __init__.py named incorrectly as __init.py__ — renamed

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
        conftest.py       ← setup_app_role, db_session, app_session, two_tenants
        unit/
            test_rls.py   ← TestRLS class with 3 tests

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
(public)     → /, /pricing, /about, /contact
(auth)       → /sign-in, /sign-up
(onboarding) → /onboarding
(portal)     → /dashboard, /gdpr, /nis2, /ai-act,
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
    packages/common/common/auth/__init__.py
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
- Created packages/common/common/db/__init__.py
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
- Updated common/db/__init__.py to export get_tenant_session
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


| Topic | Decision | Rationale |
|---|---|---|
| Monorepo style | Flat `services/` layout | Simpler than Turborepo for Python-heavy stack |
| Auth | Clerk | Org/role primitives fit multi-tenancy |
| DB isolation | PostgreSQL RLS | Defence-in-depth — app layer + DB layer |
| Backend framework | FastAPI | Async-native, OpenAPI, type hints |
| Python package manager | `uv` | 10-100x faster than pip, lockfile-based |
| Node package manager | `pnpm` | Strict mode, no phantom dependencies |
| Deployment | Railway | Per-service deploy model fits microservices |
| Commit format | Conventional Commits | Feeds automated changelog + semver |
| Branch strategy | Trunk-based off `main` | Linear history, short-lived branches |