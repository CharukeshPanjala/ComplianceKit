# ── Docker (all services) ─────────────────────────────────
up:
	docker compose -f infrastructure/docker/docker-compose.yml up -d

down:
	docker compose -f infrastructure/docker/docker-compose.yml down

restart:
	docker compose -f infrastructure/docker/docker-compose.yml restart

rebuild:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build

logs:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f

# ── API Gateway ───────────────────────────────────────────
up-api:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build api-gateway

down-api:
	docker compose -f infrastructure/docker/docker-compose.yml stop api-gateway

restart-api:
	docker compose -f infrastructure/docker/docker-compose.yml restart api-gateway

rebuild-api:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build api-gateway

logs-api:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f api-gateway

# ── Policy Engine ─────────────────────────────────────────
up-policy:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build policy-engine

down-policy:
	docker compose -f infrastructure/docker/docker-compose.yml stop policy-engine

restart-policy:
	docker compose -f infrastructure/docker/docker-compose.yml restart policy-engine

rebuild-policy:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build policy-engine

logs-policy:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f policy-engine

# ── Document Generator ────────────────────────────────────
up-docs:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build document-generator

down-docs:
	docker compose -f infrastructure/docker/docker-compose.yml stop document-generator

restart-docs:
	docker compose -f infrastructure/docker/docker-compose.yml restart document-generator

rebuild-docs:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build document-generator

logs-docs:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f document-generator

# ── DSAR Service ──────────────────────────────────────────
up-dsar:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build dsar-service

down-dsar:
	docker compose -f infrastructure/docker/docker-compose.yml stop dsar-service

restart-dsar:
	docker compose -f infrastructure/docker/docker-compose.yml restart dsar-service

rebuild-dsar:
	docker compose -f infrastructure/docker/docker-compose.yml up -d --build dsar-service

logs-dsar:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f dsar-service

# ── Frontend ──────────────────────────────────────────────
frontend:
	cd frontend && npm run dev

# ── Database ──────────────────────────────────────────────
migrate:
	docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway uv run alembic -c /app/packages/common/alembic.ini upgrade head
migrate-down:
	docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway uv run alembic -c /app/packages/common/alembic.ini downgrade -1
db:
	docker exec -it compliancekit-postgres psql -U postgres -d compliancekit

# ── Tests ─────────────────────────────────────────────────
lint-fields:
	uv run python packages/common/scripts/lint_profile_fields.py

test:
	uv run python packages/common/scripts/lint_profile_fields.py
	uv run pytest packages/common/tests/ -v
	uv run pytest services/api-gateway/tests/ -v
	uv run pytest services/policy-engine/tests/ -v

test-api:
	uv run pytest services/api-gateway/tests/ -v

test-common:
	uv run pytest packages/common/tests/ -v

# ── Dev (full stack) ──────────────────────────────────────
dev:
	make up
	cd frontend && npm run dev

.PHONY: up down restart rebuild logs \
	up-api down-api restart-api rebuild-api logs-api \
	up-policy down-policy restart-policy rebuild-policy logs-policy \
	up-docs down-docs restart-docs rebuild-docs logs-docs \
	up-dsar down-dsar restart-dsar rebuild-dsar logs-dsar \
	frontend migrate migrate-down db test test-api test-common dev

# ── Seeders ───────────────────────────────────────────────
seed:
	cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit uv run python scripts/seeders/seed_all.py

seed-gdpr:
	cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit uv run python scripts/seeders/seed_gdpr.py

seed-nis2:
	cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit uv run python scripts/seeders/seed_nis2.py

seed-euai:
	cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit uv run python scripts/seeders/seed_eu_ai_act.py

seed-embeddings:
	cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit uv run python scripts/seeders/seed_embeddings.py