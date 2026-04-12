# ComplianceKit — Dev Log

Running diary of progress, decisions, and blockers across all sprints.
Updated every time a ticket is closed.

---

## Sprint 0 — Foundation

**Goal:** Get the monorepo scaffolded, documented, and pushed to GitHub. No application code yet — just structure, tooling config, and conventions.

---

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

## Notes & Ongoing Decisions

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