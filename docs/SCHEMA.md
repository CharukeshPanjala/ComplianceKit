# ComplianceKit — Database Schema

Complete database schema for the ComplianceKit platform. Every table is designed with multi-tenancy as a first-class concern — all tenant data is isolated at the database level via PostgreSQL Row Level Security (RLS).

---

## Schema Diagram

```mermaid
erDiagram

    TENANTS {
        uuid id PK
        string tenant_id UK
        string name
        string slug UK
        enum plan
        jsonb enabled_regulations
        jsonb assessment_config
        timestamp created_at
        timestamp updated_at
    }

    USERS {
        uuid id PK
        string user_id UK
        string tenant_id FK
        string tenant_name
        string email UK
        enum role
        jsonb permissions
        enum status
        string invited_by
        timestamp last_login_at
        timestamp created_at
        timestamp updated_at
    }

    COMPANY_PROFILES {
        uuid id PK
        string profile_id UK
        string tenant_id FK
        string tenant_name
        enum industry
        enum company_size
        enum b2b_or_b2c
        enum number_of_data_subjects
        enum data_role
        string website_url
        string primary_jurisdiction
        boolean uses_cloud_services
        jsonb cloud_providers
        string primary_cloud_region
        boolean has_on_premise_servers
        jsonb certifications
        boolean has_compliance_officer
        string dpo_name
        string dpo_email
        string legal_contact_email
        jsonb data_categories_processed
        jsonb processing_purposes
        jsonb data_subject_categories
        jsonb tech_stack
        date last_audit_date
        boolean previous_regulatory_action
        string regulatory_authority
        jsonb gdpr_data
        jsonb nis2_data
        jsonb ai_act_data
        boolean is_complete
        timestamp completed_at
        timestamp created_at
        timestamp updated_at
    }

    COMPANY_PROFILE_VERSIONS {
        uuid id PK
        string version_id UK
        string tenant_id FK
        string tenant_name
        string profile_id FK
        int version_number
        enum industry
        enum company_size
        jsonb gdpr_data
        jsonb nis2_data
        jsonb ai_act_data
        jsonb changed_fields
        string changed_by FK
        string change_reason
        timestamp created_at
    }

    REGULATIONS {
        uuid id PK
        string regulation_id UK
        string name
        string full_name
        text description
        string jurisdiction
        string authority
        string current_version
        date effective_date
        date review_date
        enum status
        string source_url
        timestamp last_checked_at
        timestamp created_at
        timestamp updated_at
    }

    REGULATION_VERSIONS {
        uuid id PK
        string version_id UK
        string regulation_id FK
        string version_number
        string version_label
        date effective_date
        date superseded_date
        text changes_summary
        jsonb changed_articles
        enum impact_level
        enum detected_by
        timestamp created_at
    }

    RULES {
        uuid id PK
        string rule_id UK
        string regulation_id FK
        string regulation_version_id FK
        string current_version_id FK
        string article
        int article_number
        string article_paragraph
        string title
        text description
        text plain_english
        enum severity
        string fine_tier
        string check_type
        string profile_field
        jsonb evaluation_logic
        text remediation_hint
        jsonb remediation_steps
        jsonb remediation_resources
        jsonb applicability_tags
        boolean applies_to_b2c
        boolean applies_to_b2b
        jsonb applies_to_sizes
        boolean is_mandatory
        boolean requires_special_data
        boolean is_active
        vector embedding
        timestamp deprecated_at
        timestamp created_at
        timestamp updated_at
    }

    RULE_VERSIONS {
        uuid id PK
        string version_id UK
        string rule_id FK
        string regulation_version_id FK
        int version_number
        string article
        text description
        text plain_english
        enum severity
        jsonb evaluation_logic
        text remediation_hint
        jsonb remediation_steps
        enum change_type
        text change_summary
        timestamp created_at
    }

    ASSESSMENTS {
        uuid id PK
        string assessment_id UK
        string tenant_id FK
        string regulation_id FK
        string regulation_name
        string regulation_version_id FK
        uuid previous_assessment_id FK
        jsonb profile_snapshot
        int score
        enum risk_level
        enum status
        string triggered_by FK
        int total_rules
        int applicable_rules
        int met_rules
        int partial_rules
        int not_met_rules
        int unknown_rules
        timestamp expires_at
        timestamp completed_at
        timestamp created_at
        timestamp updated_at
    }

    GAPS {
        uuid id PK
        string gap_id UK
        string tenant_id FK
        uuid assessment_id FK
        uuid rule_id FK
        uuid regulation_id FK
        uuid regulation_version_id FK
        string regulation_name
        string article
        int article_number
        string chapter
        string category
        string severity
        string fine_tier
        string title
        text plain_english
        text remediation_hint
        enum status
        float score
        jsonb evidence
        enum remediation_priority
        jsonb remediation_steps
        jsonb remediation_resources
        boolean resolved
        timestamp resolved_at
        string resolved_by FK
        string notes
        string assigned_to
        date due_date
        timestamp created_at
        timestamp updated_at
    }

    ROPA_ENTRIES {
        uuid id PK
        string public_id UK
        string tenant_id FK
        uuid regulation_id FK
        uuid source_profile_id FK
        string category
        enum data_role
        text activity_name
        text purpose
        enum legal_basis
        text legal_obligation_reference
        text legitimate_interest_description
        array data_categories
        array data_subject_categories
        boolean has_special_category_data
        array special_category_types
        enum special_category_condition
        boolean has_automated_decision_making
        text automated_decision_description
        jsonb recipient_categories
        array processing_locations
        jsonb third_party_transfers
        enum transfer_mechanism
        jsonb processors
        text retention_period
        text security_measures
        boolean requires_dpia
        boolean dpia_completed
        enum status
        enum source
        timestamp last_reviewed_at
        date next_review_date
        string reviewed_by FK
        string approved_by FK
        timestamp approved_at
        string created_by FK
        string updated_by FK
        timestamp created_at
        timestamp updated_at
    }

    POLICIES {
        uuid id PK
        string policy_id UK
        string tenant_id FK
        string tenant_name
        string title
        enum type
        enum status
        string language
        enum content_format
        int current_version
        text content
        array tags
        boolean is_ai_enhanced
        uuid regulation_id FK
        uuid assessment_id FK
        string related_article
        string created_by FK
        string reviewed_by FK
        string approved_by FK
        timestamp approved_at
        date next_review_date
        timestamp created_at
        timestamp updated_at
    }

    POLICY_VERSIONS {
        uuid id PK
        string version_id UK
        string tenant_id FK
        string tenant_name
        string policy_id FK
        int version_number
        enum status
        string language
        enum content_format
        string title
        text content
        boolean is_ai_enhanced
        text change_summary
        enum change_type
        jsonb changed_fields
        string created_by FK
        string reviewed_by FK
        string approved_by FK
        timestamp approved_at
        timestamp created_at
    }

    DSAR_REQUESTS {
        uuid id PK
        string dsar_id UK
        string tenant_id FK
        string tenant_name
        string subject_email
        string subject_name
        boolean subject_verified
        enum verification_method
        timestamp verified_at
        string verified_by FK
        enum type
        text description
        enum status
        timestamp deadline_at
        timestamp extended_deadline_at
        text extension_reason
        timestamp extension_notified_at
        int days_remaining
        string assigned_to FK
        timestamp assigned_at
        text response_notes
        timestamp response_sent_at
        enum rejection_reason
        text rejection_notes
        jsonb data_categories_found
        jsonb data_location
        timestamp withdrawn_at
        text withdrawal_reason
        timestamp created_at
        timestamp updated_at
        timestamp fulfilled_at
    }

    DOCUMENTS {
        uuid id PK
        string document_id UK
        string tenant_id FK
        string tenant_name
        string title
        enum type
        enum format
        string language
        string policy_id FK
        string policy_version_id FK
        string assessment_id FK
        string dsar_id FK
        string storage_url
        string storage_key
        int file_size_bytes
        string checksum
        string generated_by FK
        boolean is_ai_enhanced
        int generation_time_ms
        string template_used
        boolean is_public
        string access_url
        timestamp access_expires_at
        int download_count
        timestamp created_at
        timestamp expires_at
    }

    %% Relationships

    TENANTS ||--o{ USERS : "has many"
    TENANTS ||--o| COMPANY_PROFILES : "has one"
    TENANTS ||--o{ ASSESSMENTS : "has many"
    TENANTS ||--o{ ROPA_ENTRIES : "has many"
    TENANTS ||--o{ POLICIES : "has many"
    TENANTS ||--o{ DSAR_REQUESTS : "has many"
    TENANTS ||--o{ DOCUMENTS : "has many"
    TENANTS ||--o{ GAPS : "has many"

    COMPANY_PROFILES ||--o{ COMPANY_PROFILE_VERSIONS : "has many"
    COMPANY_PROFILES ||--o{ ROPA_ENTRIES : "generated from"

    REGULATIONS ||--o{ REGULATION_VERSIONS : "has many"
    REGULATIONS ||--o{ RULES : "has many"
    REGULATIONS ||--o{ ASSESSMENTS : "has many"
    REGULATIONS ||--o{ ROPA_ENTRIES : "has many"
    REGULATIONS ||--o{ POLICIES : "has many"

    REGULATION_VERSIONS ||--o{ RULES : "has many"
    REGULATION_VERSIONS ||--o{ RULE_VERSIONS : "has many"
    REGULATION_VERSIONS ||--o{ ASSESSMENTS : "has many"

    RULES ||--o{ RULE_VERSIONS : "has many"
    RULES ||--o{ GAPS : "has many"

    ASSESSMENTS ||--o{ GAPS : "has many"
    ASSESSMENTS ||--o{ DOCUMENTS : "has many"
    ASSESSMENTS ||--o{ POLICIES : "triggered"

    POLICIES ||--o{ POLICY_VERSIONS : "has many"
    POLICIES ||--o{ DOCUMENTS : "has many"

    DSAR_REQUESTS ||--o{ DOCUMENTS : "has many"
```

---

## Table Descriptions

### 1. tenants

**Purpose:** One row per company using ComplianceKit. The root of the entire data model — every other table with `tenant_id` belongs to a tenant.

**Key design decisions:**

- `enabled_regulations` JSONB controls which regulations the tenant has access to. Adding a new regulation requires no schema migration — just a new key in the JSON.
- `assessment_config` JSONB stores scheduling preferences. Flexible enough to add new config options without migrations.
- No compliance data here — that lives in `company_profiles`. Tenants is identity and billing only.

| Column              | Type   | Description                                      |
| ------------------- | ------ | ------------------------------------------------ |
| id                  | UUID   | Internal primary key, never exposed in API       |
| tenant_id           | STRING | Clerk org ID, used as PK in tenant tables        |
| name                | STRING | Company full name e.g. "Acme GmbH"               |
| slug                | STRING | URL-friendly name e.g. "acme-gmbh"               |
| plan                | ENUM   | free / pro / enterprise                          |
| enabled_regulations | JSONB  | `{"gdpr": true, "nis2": false, "ai_act": false}` |
| assessment_config   | JSONB  | `{"auto_run": false, "schedule": "monthly"}`     |

---

### 2. users

**Purpose:** One row per person who has access to a tenant account. Managed by Clerk for auth — this table mirrors Clerk user data and adds ComplianceKit-specific fields.

**Key design decisions:**

- `tenant_name` is denormalised here to avoid joins when displaying user lists.
- Invite lifecycle delegated to Clerk — no invite tokens stored here.
- `permissions` JSONB stores overrides from the default role permissions. Only changed fields are stored — the application code falls back to role defaults.

| Column      | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| user_id     | STRING | Clerk user ID, used as PK                |
| tenant_id   | STRING | Which company this user belongs to       |
| tenant_name | STRING | Denormalised from tenants.name           |
| email       | STRING | Unique across the entire platform        |
| role        | ENUM   | admin / member / viewer                  |
| permissions | JSONB  | Custom permission overrides set by admin |
| status      | ENUM   | pending / active / suspended             |
| invited_by  | STRING | user_id of who sent the invite           |

---

### 3. company_profiles

**Purpose:** Stores everything about a company's compliance posture. This is the input to the gap analysis engine — every field maps to one or more regulation requirements.

**Key design decisions:**

- `gdpr_data`, `nis2_data`, `ai_act_data` are JSONB to allow adding new regulation-specific fields without schema migrations.
- Core fields (industry, size, jurisdiction) stay as typed columns because the gap engine filters rules based on them.
- `is_complete` gates gap analysis — engine only runs on completed profiles.
- `data_role` (controller / processor / both) drives applicability filtering — processors skip controller-only obligations.
- Adding a new regulation (e.g. Data Act) = add a `data_act_data` JSONB column. One migration, then all future fields are flexible.

| Column                  | Type   | Description                                                                            |
| ----------------------- | ------ | -------------------------------------------------------------------------------------- |
| profile_id              | STRING | Public ID e.g. `cp_2kx7m9p1`                                                           |
| tenant_id               | STRING | Which company this profile belongs to                                                  |
| industry                | ENUM   | technology / healthcare / finance / legal / retail / education / manufacturing / other |
| company_size            | ENUM   | 1-10 / 11-50 / 51-200 / 201-1000 / 1000+                                               |
| b2b_or_b2c              | ENUM   | b2b / b2c / both                                                                       |
| number_of_data_subjects | ENUM   | under_1k / under_10k / under_100k / over_100k                                          |
| data_role               | ENUM   | controller / processor / both                                                          |
| primary_jurisdiction    | STRING | Country code e.g. DE, FR, IE                                                           |
| tech_stack              | JSONB  | List of SaaS tool names from onboarding step 2                                         |
| gdpr_data               | JSONB  | GDPR-specific compliance fields (lawful bases, transfers, processors etc.)             |
| nis2_data               | JSONB  | NIS2-specific compliance fields (sectors, entity type etc.)                            |
| ai_act_data             | JSONB  | EU AI Act-specific compliance fields (uses_ai, role, high_risk_categories etc.)        |
| is_complete             | BOOL   | Whether profile is complete enough to run analysis                                     |

---

### 4. company_profile_versions

**Purpose:** Full audit trail of every change to a company profile. Required for compliance — auditors ask "what was your data processing policy in January?"

**Key design decisions:**

- Complete snapshot approach — every version stores all fields, not just what changed. Slower to write but simple to read any historical state.
- `changed_fields` JSONB records which fields changed so the UI can show a diff without comparing two full snapshots.

| Column         | Type   | Description                                                   |
| -------------- | ------ | ------------------------------------------------------------- |
| version_id     | STRING | Public ID e.g. `cpv_xxx`                                      |
| profile_id     | STRING | Which profile this version belongs to                         |
| version_number | INT    | Increments with each change                                   |
| changed_fields | JSONB  | Which fields changed e.g. `["gdpr_data.has_dpo", "industry"]` |
| changed_by     | STRING | user_id who made the change                                   |
| change_reason  | STRING | Optional note explaining why                                  |

---

### 5. regulations

**Purpose:** Global registry of all regulations ComplianceKit supports. No tenant_id — regulations are shared across the entire platform.

**Key design decisions:**

- `status` controls what appears in the dashboard — `coming_soon` shows a locked card, `active` shows live data.
- `source_url` points to the official EU source for monitoring updates.
- Adding a new regulation = insert one row. No code changes needed.

| Column          | Type   | Description                                |
| --------------- | ------ | ------------------------------------------ |
| regulation_id   | STRING | Public ID e.g. `reg_xxx`                   |
| name            | STRING | GDPR / NIS2 / EU_AI_ACT                    |
| full_name       | STRING | "General Data Protection Regulation"       |
| jurisdiction    | STRING | EU / UK / Global                           |
| authority       | STRING | "European Data Protection Board"           |
| current_version | STRING | Points to latest version e.g. "2024.1"     |
| status          | ENUM   | active / coming_soon / deprecated          |
| source_url      | STRING | Official source URL for monitoring updates |

---

### 6. regulation_versions

**Purpose:** History of every change to a regulation. Links regulations to the specific version rules and assessments were evaluated against.

**Key design decisions:**

- `superseded_date` marks when this version was replaced. Null means still active.
- `changed_articles` lets the system flag tenants: "Article 17 was updated — your assessment may be outdated."
- `detected_by` tracks whether the update was found manually or via automated monitoring.

| Column           | Type   | Description                                     |
| ---------------- | ------ | ----------------------------------------------- |
| version_id       | STRING | Public ID e.g. `rgv_xxx`                        |
| regulation_id    | STRING | Which regulation this version belongs to        |
| version_number   | STRING | e.g. "2018.1", "2024.1"                         |
| effective_date   | DATE   | When this version took effect                   |
| superseded_date  | DATE   | When replaced by newer version, null if current |
| changed_articles | JSONB  | `["Article 5", "Article 17"]`                   |
| impact_level     | ENUM   | minor / moderate / major                        |
| detected_by      | ENUM   | manual / automated / partner_feed               |

---

### 7. rules

**Purpose:** Every individual compliance requirement across all regulations. The brain of the gap engine — tells it what to check, how serious a failure is, and how to remediate.

**Key design decisions:**

- `fine_tier` and `severity` are separate — fine exposure doesn't always map 1:1 to operational severity.
- `check_type` = `informational` rules are never scored — they're awareness only.
- `applicability_tags` JSONB used by the applicability engine for fast rule filtering by profile characteristics.
- `embedding` (pgvector) enables semantic search over rule text — used by DPO Assistant RAG (COM-187).
- `plain_english` keeps legal jargon out of the UI.

| Column                | Type    | Description                                             |
| --------------------- | ------- | ------------------------------------------------------- |
| rule_id               | STRING  | Public ID e.g. `rul_xxx`                                |
| regulation_id         | STRING  | Which regulation this rule belongs to                   |
| regulation_version_id | STRING  | Which regulation version introduced this rule           |
| article               | STRING  | e.g. "Article 37"                                       |
| article_number        | INT     | Numeric for sorting e.g. 37                             |
| severity              | ENUM    | critical / high / medium / low                          |
| fine_tier             | STRING  | tier_1 (2% global turnover) / tier_2 (4%)               |
| check_type            | STRING  | profile_field / document / informational                |
| is_mandatory          | BOOL    | Whether this rule is mandatory regardless of profile    |
| profile_field         | STRING  | Which company_profiles field to evaluate                |
| remediation_hint      | TEXT    | What to do to fix this gap                              |
| applicability_tags    | JSONB   | Fast filter tags used by applicability engine           |
| applies_to_b2c        | BOOL    | Whether rule applies to B2C companies                   |
| applies_to_b2b        | BOOL    | Whether rule applies to B2B companies                   |
| embedding             | VECTOR  | pgvector embedding for semantic search (COM-187)        |

---

### 8. rule_versions

**Purpose:** History of every change to a rule. Ensures assessments are permanently linked to the exact rule text that was active when they ran.

**Key design decisions:**

- `change_type` determines what action to take — `text_update` needs no reassessment, `logic_change` triggers full reassessment for all tenants.
- Complete snapshot — stores all rule fields at the time of the version, not just what changed.

| Column                | Type   | Description                                                          |
| --------------------- | ------ | -------------------------------------------------------------------- |
| version_id            | STRING | Public ID e.g. `rlv_xxx`                                             |
| rule_id               | STRING | Which rule this version belongs to                                   |
| regulation_version_id | STRING | Which regulation version this rule version belongs to                |
| version_number        | INT    | Increments with each change                                          |
| change_type           | ENUM   | text_update / severity_change / logic_change / new_rule / deprecated |
| evaluation_logic      | JSONB  | Snapshot of evaluation logic at this version                         |

---

### 9. assessments

**Purpose:** One row per compliance check run for a tenant. Stores the score, risk level, gap counts, and a snapshot of the profile at the time of assessment.

**Key design decisions:**

- `profile_snapshot` JSONB captures the full profile at assessment time — future profile changes don't retroactively alter historical assessments.
- `regulation_version_id` permanently stamps which regulation version was active.
- `risk_level` (critical / high / medium / low) is pre-calculated from score for fast dashboard display.
- `previous_assessment_id` enables score trend calculation without querying history.

| Column                | Type   | Description                                    |
| --------------------- | ------ | ---------------------------------------------- |
| assessment_id         | STRING | Public ID e.g. `asm_xxx`                        |
| tenant_id             | STRING | Which company this assessment belongs to        |
| regulation_id         | STRING | Which regulation was assessed                   |
| regulation_version_id | STRING | Which version was active when this ran          |
| profile_snapshot      | JSONB  | Full profile at time of assessment              |
| score                 | FLOAT  | Compliance score 0-100                          |
| risk_level            | ENUM   | critical / high / medium / low                  |
| status                | ENUM   | pending / running / completed / failed          |
| total_rules           | INT    | Total rules evaluated                           |
| applicable_rules      | INT    | Rules applicable to this company                |
| met_rules             | INT    | Rules fully met                                 |
| partial_rules         | INT    | Rules partially met                             |
| not_met_rules         | INT    | Rules not met (gaps)                            |

---

### 10. gaps

**Purpose:** Every individual compliance failure found in an assessment. Drives the gap list, remediation roadmap, and score calculation.

**Key design decisions:**

- `article`, `title`, `plain_english`, `regulation_name` are denormalised so gaps remain readable even after rule updates.
- `evidence` JSONB captures why the engine marked this gap — useful for auditors and appeals.
- `remediation_priority` (critical / high / medium / low) is separate from severity — an easy win might be low severity but high priority.
- `resolved` boolean with `resolved_at` timestamp enables gap management workflow without deleting rows.

| Column               | Type   | Description                                        |
| -------------------- | ------ | -------------------------------------------------- |
| gap_id               | STRING | Public ID e.g. `gap_xxx`                           |
| assessment_id        | UUID   | Which assessment found this gap                    |
| rule_id              | UUID   | Which rule was failed                              |
| regulation_name      | STRING | Denormalised e.g. "GDPR"                           |
| article              | STRING | e.g. "Article 37"                                  |
| severity             | ENUM   | critical / high / medium / low                     |
| status               | ENUM   | met / partial / not_met / unknown / not_applicable |
| score                | FLOAT  | Rule score 0-1                                     |
| evidence             | JSONB  | Why the engine scored this way                     |
| remediation_priority | ENUM   | critical / high / medium / low                     |
| resolved             | BOOL   | Whether the gap has been resolved                  |
| resolved_at          | TIMESTAMP | When resolved                                   |
| notes                | STRING | Free-text notes from compliance officer            |
| due_date             | DATE   | Target resolution date                             |

---

### 11. ropa_entries

**Purpose:** GDPR Article 30 Records of Processing Activities. Each row = one processing activity (e.g. "Marketing and Communications", "HR Data Processing"). Can be auto-generated from company profile or created manually. Driven by COM-172/173.

**Key design decisions:**

- `source` (auto_generated / manual) distinguishes generator output from user-created entries — regenerating only deletes AUTO_GENERATED rows, never MANUAL ones.
- `transfer_mechanism` documents the Art. 46 legal basis for EEA→outside transfers (SCCs, BCRs, adequacy decision, etc.).
- `special_category_condition` records which Art. 9(2) exemption applies — required when processing health, biometric, genetic etc. data.
- `requires_dpia` is set automatically by the generator when special category data + large scale; user can override.
- `source_profile_id` links auto-generated entries to the profile snapshot they were built from.
- RLS enforced — tenants can only see their own entries.

| Column                      | Type   | Description                                                                    |
| --------------------------- | ------ | ------------------------------------------------------------------------------ |
| public_id                   | STRING | Public ID e.g. `rop_xxx`                                                       |
| tenant_id                   | STRING | Which company this entry belongs to                                            |
| regulation_id               | UUID   | Always GDPR (Art. 30 requirement)                                              |
| source_profile_id           | UUID   | Profile this was generated from (nullable for manual entries)                  |
| activity_name               | TEXT   | e.g. "Marketing and Communications"                                            |
| purpose                     | TEXT   | Processing purpose slug e.g. "marketing"                                       |
| category                    | STRING | Activity category e.g. "marketing", "hr", "analytics"                         |
| data_role                   | ENUM   | controller / processor                                                         |
| legal_basis                 | ENUM   | consent / contract / legal_obligation / vital_interests / public_task / legitimate_interests |
| legal_obligation_reference  | TEXT   | If legal_obligation — which law? e.g. "Employment Act 2002"                    |
| legitimate_interest_description | TEXT | If legitimate_interests — what's the interest?                              |
| data_categories             | ARRAY  | e.g. ["email", "name", "health"]                                               |
| data_subject_categories     | ARRAY  | e.g. ["customers", "employees"]                                                |
| has_special_category_data   | BOOL   | Whether Art. 9 special category data is processed                              |
| special_category_types      | ARRAY  | Which special types e.g. ["health", "biometric"]                               |
| special_category_condition  | ENUM   | Art. 9(2) condition: explicit_consent / employment_law / vital_interests / non_profit / made_public / legal_claims / public_interest / health_care / public_health / research |
| has_automated_decision_making | BOOL | Whether Art. 22 automated decisions apply                                      |
| processing_locations        | ARRAY  | Where data is processed e.g. ["IE", "aws", "gcp"]                              |
| third_party_transfers       | JSONB  | Details of transfers outside EEA                                               |
| transfer_mechanism          | ENUM   | scc / bcr / adequacy_decision / derogation / none                              |
| processors                  | JSONB  | Third-party processors used e.g. {"tools": ["Salesforce", "Mailchimp"]}        |
| retention_period            | TEXT   | e.g. "2 years after contract end"                                              |
| security_measures           | TEXT   | Summary of technical/organisational measures                                   |
| requires_dpia               | BOOL   | Whether a DPIA (Art. 35) is required                                           |
| dpia_completed              | BOOL   | Whether the DPIA has been completed                                            |
| status                      | ENUM   | draft / active / archived                                                      |
| source                      | ENUM   | auto_generated / manual                                                        |
| next_review_date            | DATE   | When this entry should next be reviewed                                        |

---

### 12. policies

**Purpose:** Compliance documents a company creates — privacy notices, DPAs, cookie policies, data retention policies etc. The gap engine checks for active policies to auto-close related gaps.

**Key design decisions:**

- `regulation_id` links each policy to the regulation it satisfies — enables the gap engine to auto-close gaps when the right policy exists.
- `assessment_id` links to the assessment that triggered this policy being needed — tracks which gaps drove the policy creation.
- `content_format` (markdown / plain_text) tells the editor how to render the content — AI-generated policies use markdown.
- `tags` array enables policy library filtering by topic in the COM-176 UI.
- `next_review_date` drives the deadline reminders widget.
- `is_ai_enhanced` tracks AI involvement for audit purposes.
- `current_version` is a denormalised int pointing to the latest policy_version — avoids joins for the common "show current policy" case.

| Column           | Type   | Description                                                                                              |
| ---------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| policy_id        | STRING | Public ID e.g. `pol_xxx`                                                                                 |
| tenant_id        | STRING | Which company this policy belongs to                                                                     |
| title            | STRING | e.g. "Privacy Notice", "Data Processing Agreement"                                                       |
| type             | ENUM   | privacy_notice / ropa / dpa / cookie_policy / data_retention / incident_response / ai_governance / other |
| status           | ENUM   | draft / active / under_review / archived                                                                 |
| content_format   | ENUM   | markdown / plain_text                                                                                    |
| language         | STRING | e.g. "en", "de", "fr"                                                                                    |
| tags             | ARRAY  | e.g. ["gdpr", "article-13", "privacy"]                                                                   |
| regulation_id    | UUID   | Which regulation this policy satisfies (nullable)                                                        |
| assessment_id    | UUID   | Assessment that triggered this policy (nullable)                                                         |
| related_article  | STRING | e.g. "Article 13"                                                                                        |
| current_version  | INT    | Points to latest version number                                                                          |
| content          | TEXT   | Denormalised current version content for fast reads                                                      |
| is_ai_enhanced   | BOOL   | Whether AI was used to generate/improve                                                                  |
| next_review_date | DATE   | When this policy needs reviewing                                                                         |
| approved_by      | STRING | user_id who approved this policy                                                                         |

---

### 13. policy_versions

**Purpose:** Full version history of every policy. Auditors can see exactly what a policy said on any given date.

**Key design decisions:**

- Each version has its own approval record — the system knows which version was last formally approved.
- `change_type` categorises the reason for the new version.
- `content_format` mirrors the parent policy format — stored per-version in case format changes over time.
- Documents table links to `policy_version_id` — generated PDFs are permanently linked to the exact version they were generated from.

| Column         | Type   | Description                                                        |
| -------------- | ------ | ------------------------------------------------------------------ |
| version_id     | STRING | Public ID e.g. `ver_xxx`                                           |
| policy_id      | STRING | Which policy this version belongs to                               |
| version_number | INT    | Increments with each change                                        |
| content_format | ENUM   | markdown / plain_text                                              |
| content        | TEXT   | Full policy text at this version                                   |
| change_type    | ENUM   | created / edited / ai_enhanced / approved / archived               |
| change_summary | TEXT   | Human-readable summary of what changed                             |
| changed_fields | JSONB  | Which fields changed                                               |
| is_ai_enhanced | BOOL   | Whether this version was AI-generated or AI-improved               |
| approved_by    | STRING | user_id who approved this version                                  |

---

### 14. dsar_requests

**Purpose:** Full lifecycle management of Data Subject Access Requests. Tracks every DSAR from intake to fulfilment with GDPR-compliant deadline enforcement.

**Key design decisions:**

- `deadline_at` is always 30 days from `created_at` per GDPR Article 12.
- `extended_deadline_at` supports the 2-month extension allowed under Article 12(3).
- `extension_notified_at` proves the subject was notified of the extension within 1 month — a specific GDPR requirement.
- `days_remaining` is a calculated field updated daily by a background job — fast dashboard queries.
- `rejection_reason` is an enum — GDPR only allows rejection for specific legal reasons.

| Column                | Type      | Description                                                                   |
| --------------------- | --------- | ----------------------------------------------------------------------------- |
| dsar_id               | STRING    | Public ID e.g. `dsr_xxx`                                                      |
| type                  | ENUM      | access / deletion / portability / rectification / restriction / objection     |
| status                | ENUM      | pending / verified / processing / fulfilled / rejected / extended / withdrawn |
| deadline_at           | TIMESTAMP | 30 days from created_at                                                       |
| extended_deadline_at  | TIMESTAMP | Up to 2 extra months                                                          |
| days_remaining        | INT       | Calculated daily by background job                                            |
| rejection_reason      | ENUM      | cannot_verify_identity / manifestly_unfounded / excessive / not_applicable    |
| data_categories_found | JSONB     | What data was found about the subject                                         |
| data_location         | JSONB     | Where data was found                                                          |

---

### 15. documents

**Purpose:** Every generated compliance document — PDFs, DOCX files, Markdown exports. Links back to the exact source (policy version, assessment, or DSAR) it was generated from.

**Key design decisions:**

- `policy_version_id` links to the exact policy version used — the document can be reproduced identically even after the policy is updated.
- `checksum` enables file integrity verification — proves a document hasn't been tampered with.
- `is_public` marks documents like privacy notices that must be publicly accessible.
- `access_url` is a signed URL with expiry — secure sharing without making storage buckets public.
- Documents can come from three sources — policy (policy_id set), assessment (assessment_id set), or DSAR (dsar_id set).

| Column            | Type      | Description                                                                                                                                  |
| ----------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| document_id       | STRING    | Public ID e.g. `doc_xxx`                                                                                                                     |
| type              | ENUM      | ropa / privacy_notice / dpa / cookie_policy / data_retention / incident_response / ai_governance / dsar_response / assessment_report / other |
| format            | ENUM      | pdf / docx / markdown                                                                                                                        |
| policy_version_id | STRING    | Exact policy version used to generate                                                                                                        |
| assessment_id     | STRING    | Assessment this document was generated from                                                                                                  |
| dsar_id           | STRING    | DSAR this document was generated for                                                                                                         |
| checksum          | STRING    | File integrity hash                                                                                                                          |
| is_public         | BOOL      | Whether publicly accessible                                                                                                                  |
| access_url        | STRING    | Signed URL for download                                                                                                                      |
| access_expires_at | TIMESTAMP | When signed URL expires                                                                                                                      |
| download_count    | INT       | Number of times downloaded                                                                                                                   |
| expires_at        | TIMESTAMP | When document itself expires                                                                                                                 |

---

## Relationships Summary

```
tenants
├── users                         (one tenant has many users)
├── company_profiles              (one tenant has one profile)
│   └── company_profile_versions  (one profile has many versions)
├── assessments                   (one tenant has many assessments)
│   └── gaps                      (one assessment has many gaps)
├── ropa_entries                  (one tenant has many ROPA entries)
├── policies                      (one tenant has many policies)
│   └── policy_versions           (one policy has many versions)
├── dsar_requests                 (one tenant has many DSARs)
└── documents                     (one tenant has many documents)

regulations (global — no tenant_id)
├── regulation_versions           (one regulation has many versions)
├── rules                         (one regulation has many rules)
│   └── rule_versions             (one rule has many versions)
└── ropa_entries                  (one regulation has many ROPA entries)

assessments
├── gaps → rules                  (gaps reference the rule that was failed)
└── policies                      (assessment triggers policy creation)

documents
├── → policy_versions             (generated from a policy version)
├── → assessments                 (generated from an assessment)
└── → dsar_requests               (generated for a DSAR response)
```

---

## Prefixed Public IDs

All public IDs use nanoid with a prefix for instant identification:

| Prefix  | Table                    | Example         |
| ------- | ------------------------ | --------------- |
| `ten_`  | tenants                  | `ten_4x7k9p2m`  |
| `usr_`  | users                    | `usr_9m3kx7p1`  |
| `cp_`   | company_profiles         | `cp_2kx7m9p1`   |
| `cpv_`  | company_profile_versions | `cpv_3mx9k7p2`  |
| `reg_`  | regulations              | `reg_7p2m9k3x`  |
| `rgv_`  | regulation_versions      | `rgv_1k9x7m2p`  |
| `rul_`  | rules                    | `rul_5m2p9k7x`  |
| `rlv_`  | rule_versions            | `rlv_8k3x2m9p`  |
| `asm_`  | assessments              | `asm_4p7k2x9m`  |
| `gap_`  | gaps                     | `gap_2x9m7k3p`  |
| `rop_`  | ropa_entries             | `rop_7k3x2m9p`  |
| `pol_`  | policies                 | `pol_7m3k9x2p`  |
| `ver_`  | policy_versions          | `ver_9k2p7m3x`  |
| `dsr_`  | dsar_requests            | `dsr_3p9x2k7m`  |
| `doc_`  | documents                | `doc_6m7k3x9p`  |

Raw UUIDs are never exposed in API responses. All external references use these prefixed IDs.

---

## Multi-tenancy

Every table with tenant data has a `tenant_id` column. PostgreSQL Row Level Security (RLS) policies enforce isolation at the database layer — not just the application layer. Even if application code has a bug that fetches the wrong data, the database will return zero rows.

The only tables without `tenant_id` are global reference tables: `regulations`, `regulation_versions`, `rules`, `rule_versions`. These are shared across all tenants and are read-only for tenants.

---

## Built Status

| Table                    | Status | Ticket      |
| ------------------------ | ------ | ----------- |
| tenants                  | ✅ Built | Sprint 0   |
| users                    | ✅ Built | Sprint 0   |
| company_profiles         | ✅ Built | Sprint 1   |
| company_profile_versions | ✅ Built | Sprint 1   |
| regulations              | ✅ Built | COM-157    |
| regulation_versions      | ✅ Built | COM-157    |
| rules                    | ✅ Built | COM-157    |
| rule_versions            | ✅ Built | COM-157    |
| assessments              | ✅ Built | COM-162    |
| gaps                     | ✅ Built | COM-162    |
| ropa_entries             | ✅ Built | COM-171    |
| policies                 | 🔲 Migration | COM-174 |
| policy_versions          | 🔲 Migration | COM-174 |
| dsar_requests            | 🔲 Migration | COM-182 |
| documents                | 🔲 Not started | COM-177+ |
