"""create_rulebook_tables

Revision ID: 9c6a4fe3c1ce
Revises: f2fc0fffc4df
Create Date: 2026-05-29 16:42:42.604931

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9c6a4fe3c1ce'
down_revision: Union[str, Sequence[str], None] = 'f2fc0fffc4df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ENUMs
    op.execute("CREATE TYPE regulationstatus AS ENUM ('active', 'coming_soon', 'deprecated')")
    op.execute("CREATE TYPE impactlevel AS ENUM ('minor', 'moderate', 'major')")
    op.execute("CREATE TYPE detectedby AS ENUM ('manual', 'automated', 'partner_feed')")
    op.execute("CREATE TYPE severity AS ENUM ('critical', 'high', 'medium', 'low')")
    op.execute("CREATE TYPE rulechangetype AS ENUM ('text_update', 'severity_change', 'logic_change', 'new_rule', 'deprecated')")

    # regulations
    op.execute("""
        CREATE TABLE regulations (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            regulation_id    VARCHAR(20) UNIQUE NOT NULL,
            name             VARCHAR(50) UNIQUE NOT NULL,
            full_name        VARCHAR(255) NOT NULL,
            jurisdiction     VARCHAR(50) NOT NULL DEFAULT 'EU',
            authority        VARCHAR(255),
            current_version  VARCHAR(50),
            effective_date   DATE,
            review_date      DATE,
            status           regulationstatus NOT NULL DEFAULT 'active',
            description      TEXT,
            source_url       VARCHAR(500),
            last_checked_at  TIMESTAMPTZ,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # regulation_versions
    op.execute("""
        CREATE TABLE regulation_versions (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id       VARCHAR(20) UNIQUE NOT NULL,
            regulation_id    UUID NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
            version_number   VARCHAR(20) NOT NULL,
            version_label    VARCHAR(50) NOT NULL,
            effective_date   DATE,
            superseded_date  DATE,
            changes_summary  TEXT,
            changed_articles JSONB,
            impact_level     impactlevel,
            detected_by      detectedby NOT NULL DEFAULT 'manual',
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # rules (without current_version_id FK — added after rule_versions to resolve circular dep)
    op.execute("""
        CREATE TABLE rules (
            id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            rule_id               VARCHAR(20) UNIQUE NOT NULL,
            regulation_id         UUID NOT NULL REFERENCES regulations(id) ON DELETE CASCADE,
            regulation_version_id UUID REFERENCES regulation_versions(id) ON DELETE SET NULL,
            current_version_id    UUID,
            article               VARCHAR(100) NOT NULL,
            article_number        INTEGER,
            article_paragraph     VARCHAR(50),
            title                 VARCHAR(500),
            chapter               VARCHAR(100),
            category              VARCHAR(100),
            description           TEXT NOT NULL,
            plain_english         TEXT,
            severity              severity NOT NULL DEFAULT 'medium',
            profile_field         VARCHAR(100),
            evaluation_logic      JSONB,
            remediation_hint      TEXT,
            remediation_steps     JSONB,
            remediation_resources JSONB,
            applicability_tags    JSONB NOT NULL DEFAULT '[]',
            applies_to_b2c        BOOLEAN NOT NULL DEFAULT true,
            applies_to_b2b        BOOLEAN NOT NULL DEFAULT true,
            applies_to_sizes      JSONB,
            requires_special_data BOOLEAN NOT NULL DEFAULT false,
            is_active             BOOLEAN NOT NULL DEFAULT true,
            deprecated_at         TIMESTAMPTZ,
            embedding             vector(1536),
            created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (regulation_id, article)
        )
    """)

    # rule_versions
    op.execute("""
        CREATE TABLE rule_versions (
            id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            version_id            VARCHAR(20) UNIQUE NOT NULL,
            rule_id               UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
            regulation_version_id UUID REFERENCES regulation_versions(id) ON DELETE SET NULL,
            version_number        INTEGER NOT NULL DEFAULT 1,
            article               VARCHAR(100),
            description           TEXT NOT NULL,
            plain_english         TEXT,
            severity              severity,
            evaluation_logic      JSONB,
            remediation_hint      TEXT,
            remediation_steps     JSONB,
            change_type           rulechangetype,
            change_summary        TEXT,
            created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Now add the circular FK: rules.current_version_id → rule_versions.id
    op.execute("""
        ALTER TABLE rules
        ADD CONSTRAINT fk_rules_current_version
        FOREIGN KEY (current_version_id) REFERENCES rule_versions(id) ON DELETE SET NULL
    """)

    # Indexes
    op.execute("CREATE INDEX regulation_versions_regulation_idx ON regulation_versions (regulation_id)")
    op.execute("CREATE INDEX rules_regulation_idx ON rules (regulation_id)")
    op.execute("CREATE INDEX rules_regulation_version_idx ON rules (regulation_version_id)")
    op.execute("CREATE INDEX rules_category_idx ON rules (category)")
    op.execute("CREATE INDEX rules_severity_idx ON rules (severity)")
    op.execute("CREATE INDEX rules_is_active_idx ON rules (is_active)")
    op.execute("CREATE INDEX rules_tags_idx ON rules USING gin (applicability_tags)")
    op.execute("CREATE INDEX rule_versions_rule_idx ON rule_versions (rule_id)")
    op.execute("CREATE INDEX rule_versions_regulation_version_idx ON rule_versions (regulation_version_id)")

    # IVFFlat cosine similarity index for RAG retrieval (COM-185/186)
    op.execute("""
        CREATE INDEX rules_embedding_idx
        ON rules USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE rules DROP CONSTRAINT IF EXISTS fk_rules_current_version")
    op.execute("DROP TABLE IF EXISTS rule_versions")
    op.execute("DROP TABLE IF EXISTS rules")
    op.execute("DROP TABLE IF EXISTS regulation_versions")
    op.execute("DROP TABLE IF EXISTS regulations")
    op.execute("DROP TYPE IF EXISTS rulechangetype")
    op.execute("DROP TYPE IF EXISTS severity")
    op.execute("DROP TYPE IF EXISTS detectedby")
    op.execute("DROP TYPE IF EXISTS impactlevel")
    op.execute("DROP TYPE IF EXISTS regulationstatus")
    op.execute("DROP EXTENSION IF EXISTS vector")