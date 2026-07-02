# EU AI Act Rule Data Audit

Audit of all 113 EU AI Act rules stored in ComplianceKit's database against the official Regulation (EU) 2024/1689 text.

## Summary

| Metric | Count |
|---|---|
| **Total articles audited** | 113 / 113 |
| **MATCH** (description + plain_english correctly capture legal meaning) | 58 |
| **PARTIAL** (mostly correct, missing nuance/exceptions/scope) | 11 |
| **MISMATCH** (wrong content, wrong title, or fabricated text not in the article) | 44 |
| **Data point needed is a gap** (NO or PARTIAL field existence) | 71 |
| **Dangling `profile_field` / `evaluation_logic` references found** | 38 articles affected, 79 individual dangling field references |

### Headline finding: systemic article numbering/content drift

Comparing every DB title against the real Regulation text revealed that **44 of 113 articles (39%)** have a title that does not match the legal content of that article number. This is not scattered noise — it clusters into three contiguous zones where the DB's content appears to have been shifted/relabeled against the wrong article number:

1. **Notified-bodies block, Articles 32–46** — titles drift but underlying description content is usually accurate for *some* nearby real article (e.g. DB Art. 32 "Subsidiaries of and subcontracting by notified bodies" is actually the content of real Article 33; real Article 32 is "Presumption of conformity with requirements relating to notified bodies").
2. **GPAI models block, Articles 51–56** — DB skips real Article 54 ("Authorised representatives of providers of GPAI models") entirely, causing Articles 52–56 to each describe the wrong real article. DB "Article 56" actually contains Annex XIII content (FLOPs/criteria for systemic risk), not real Article 56 ("Codes of practice").
3. **Governance / market-surveillance / AI Office / penalties block, Articles 61, 64–94, 99–112** — titles and content are shifted by varying, non-constant offsets. E.g. DB Article 90 "European Artificial Intelligence Board" is actually the content of real Article 65; DB Article 99 "Amendments to Regulation (EU) No 300/2008" is actually the content of real Article 102 (real Article 99 is "Penalties" — a critical mismatch since this is the article that sets the EUR 35M / 7% turnover fine for prohibited practices).

**Practical impact:** any customer-facing UI, report, or AI Office filing that cites "EU AI Act Article 99" using this DB's stored title/description for "Article 99" will tell the customer Article 99 is about an aviation security regulation amendment, when it is actually the **penalties article**. This is a high-severity content-integrity bug, independent of the dangling-field-reference bug below.

### Headline finding: dangling field references

The `evaluation_logic`/`profile_field` columns reference three field names that **do not exist** anywhere in the product's data model:

| Referenced (wrong) | Should be |
|---|---|
| `ai_act_data.high_risk_categories` | `ai_act_data.high_risk_ai_categories` |
| `ai_act_data.role` | `ai_act_data.ai_role` |
| `ai_act_data.gpai_model` | `ai_act_data.uses_gpai` |

These three typo'd field names are referenced across **38 articles** (Articles 6, 8–27, 43, 44, 47–49, 51–54, 64, 69, 71–73, 77, 86), for **79 individual occurrences** across `profile_field` + `evaluation_logic.condition`/`check`. Any assessment-engine code that evaluates these rules against the real `ai_act_data` JSONB will silently fail to match (`high_risk_categories`, `role`, `gpai_model` are not keys in the actual JSONB), meaning **every high-risk-AI and GPAI rule in the assessment engine is currently unevaluable** unless the applicability/scoring code has its own separate mapping layer that translates these names — worth checking `services/policy-engine/app/engine/applicability.py` and `scorer.py` directly.

Additionally, several `evaluation_logic.condition`/`prohibited_practices` blocks invent entirely new fields that don't exist anywhere in the field list and aren't just typos of real fields — these are full gaps, not typos:
- `is_public_body`, `provides_public_service` (Article 27)
- `uses_chatbot`, `generates_synthetic_content`, `uses_emotion_recognition` (Article 50)
- `systemic_risk` (Article 53)
- `requires_third_party_assessment` (Article 44)
- the 8 named sub-flags under Article 5's `prohibited_practices` array (`social_scoring`, `real_time_biometric_public`, `subliminal_manipulation`, `vulnerability_exploitation`, `biometric_categorisation_sensitive`, `emotion_recognition_workplace`, `facial_scraping`, `predictive_policing`) — none of these exist as granular profile fields; only the single boolean `uses_ai` exists.

---

## Chapter I — General Provisions (Articles 1–4)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 1 | Subject matter | MATCH | None (informational/scope statement) | N/A | No |
| 2 | Scope | MATCH | Whether the company builds/sells/deploys AI in the EU or whose AI output affects EU persons | YES — `ai_act_data.uses_ai` | No |
| 3 | Definitions | MATCH | None (informational) | N/A | No |
| 4 | AI literacy | MATCH | Whether an AI-literacy training programme exists for staff/contractors using AI | NO — no `has_ai_literacy_training` field; only `ai_act_data.has_ai_governance_policy` exists and is not the same thing | No |

---

## Chapter II — Prohibited AI Practices (Article 5)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 5 | Prohibited AI practices | MATCH | Description accurately lists all 8 prohibited practice categories (manipulation, vulnerability exploitation, social scoring, predictive policing, facial-scraping databases, workplace/school emotion recognition, sensitive biometric categorisation, real-time public biometric ID for law enforcement). Needed data: whether the company engages in any of these 8 specific practices | PARTIAL — only `uses_ai` boolean exists; no per-practice flags. The 8 `prohibited_practices` keys named in `evaluation_logic` (`social_scoring`, `real_time_biometric_public`, etc.) are gaps, not real fields | No (the array values aren't field refs, but they are fields that don't exist anywhere) |

---

## Chapter III, Section 1 — High-Risk Classification (Articles 6–8)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 6 | Classification rules for high-risk AI systems | PARTIAL — description omits the Article 6(3) carve-out (an Annex III system is NOT high-risk if it performs only a narrow procedural task, improves a prior human decision, detects deviations from prior patterns, or performs a preparatory task) | Whether the AI system falls into one of the 8 Annex III high-risk categories | YES (categories) — `ai_act_data.high_risk_ai_categories`, but DB references the wrong key name | YES — `ai_act_data.high_risk_categories` |
| 7 | Amendments to Annex III | MATCH | None (informational — Commission's delegated-act power) | N/A | No |
| 8 | Compliance with the requirements | MATCH | Whether company has any high-risk AI system (gates Articles 9-15 applicability) | YES (intended) | YES — `ai_act_data.high_risk_categories` (×2) |

---

## Chapter III, Section 2 — High-Risk Requirements (Articles 9–15)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 9 | Risk management system | MATCH | Whether a documented, lifecycle-wide AI risk management system exists | NO — no `has_ai_risk_management_system` field | YES |
| 10 | Data and data governance | MATCH | Whether training-data governance documentation (bias, representativeness, provenance) exists | NO — no equivalent field | YES |
| 11 | Technical documentation | MATCH | Whether Annex IV technical documentation exists for the high-risk system | NO | YES |
| 12 | Record-keeping | MATCH | Whether the AI system has automatic event/usage logging built in | NO | YES |
| 13 | Transparency and provision of information to deployers | MATCH | Whether instructions-for-use documentation (capabilities, limitations, risks) exists | NO | YES |
| 14 | Human oversight | MATCH | Whether human-oversight mechanisms (override/stop) are implemented | NO | YES |
| 15 | Accuracy, robustness and cybersecurity | MATCH | Whether the AI system has been tested for accuracy/robustness/adversarial-attack resilience | NO | YES |

All seven of these are legitimate, accurately-described high-risk provider obligations, but ComplianceKit has **zero profile fields** to capture any of them — only the high-risk-category trigger exists, not the actual compliance state for any of these substantive controls. This is the single largest cluster of real product gaps in the whole audit.

---

## Chapter III, Section 3 — Provider/Importer/Distributor Obligations (Articles 16–27)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 16 | Obligations of providers of high-risk AI systems | MATCH | Whether company is a "provider" of high-risk AI (role + conformity/CE/registration status) | PARTIAL — role exists conceptually but wrong key referenced; no field for conformity/CE/registration status | YES (`role`, ×2 incl. `high_risk_categories`) |
| 17 | Quality management system | MATCH | Whether an ISO-9001-style QMS exists for high-risk AI development | NO | YES (×2) |
| 18 | Documentation keeping | MATCH | Whether technical/QMS documentation is retained for 10 years | NO | YES (×2) |
| 19 | Automatically generated logs | **MISMATCH** — DB description fabricates a public-body-vs-private 6-months-vs-"1-3 years" split that does not appear in Article 19. The real Article 19 only says providers must retain logs "for a period appropriate to the intended purpose... of at least six months" with no public/private distinction; the public-body 6-month duty actually belongs to deployers under Article 26(6), not Article 19 | Whether log retention period/policy exists | NO | YES |
| 20 | Corrective actions and duty of information | MATCH | Whether a corrective-action/recall process exists for non-conforming AI | NO | YES (`role`) |
| 21 | Cooperation with competent authorities | MATCH | None actionable for a customer profile (regulator-facing duty) | N/A | YES (`role`) |
| 22 | Authorised representatives of providers not established in the Union | MATCH | Whether company is a non-EU provider needing an EU authorised representative | YES — `primary_jurisdiction` (correct, not dangling) | YES (in evaluation_logic: `role`) |
| 23 | Obligations of importers | MATCH | Whether company is an importer of high-risk AI systems | PARTIAL (`role` concept exists, wrong key) | YES (×2) |
| 24 | Obligations of distributors — **title note:** DB titles this "Obligations of product manufacturers"; real Article 24 is "Obligations of distributors" (real Article 24's distributor content appears, in this DB, under a different article number not directly checked) | MATCH content-wise to product-manufacturer obligations described | Whether company is a product manufacturer integrating high-risk AI | PARTIAL | YES (`role`) |
| 25 | Responsibilities along the AI value chain | MATCH | Whether company substantially modifies/rebrands a third-party AI system (which converts it into a "provider") | PARTIAL | YES (`role`) |
| 26 | Obligations of deployers of high-risk AI systems | MATCH | Whether company deploys (uses) high-risk AI under its own authority, with oversight/logging/monitoring in place | PARTIAL (`role` concept exists, no oversight/logging-policy field) | YES (×3) |
| 27 | Fundamental rights impact assessment for high-risk AI systems | MATCH | Whether deployer is a public body or private entity providing public services (education, banking, insurance, healthcare, social services) using Annex III high-risk AI | NO — `is_public_body`/`provides_public_service` don't exist; `b2b_or_b2c` and `industry` are not sufficient substitutes | YES (`high_risk_categories`, `role`) |

---

## Chapter III, Section 4 — Notifying Authorities & Notified Bodies (Articles 28–39)

All ten articles in this range (28–31, 37, 39) are **regulator/conformity-body-facing administrative procedure articles, correctly marked `profile_field: null` and `informational`** — not customer-actionable, and the descriptions for those are MATCH. However, five articles in this block have **title drift** (content describes a different real article number than the title states), even though the description text itself is legally accurate for *some* article in this neighborhood:

| # | DB Title | Real content actually matches | Verdict |
|---|---|---|---|
| 28 | Notifying authorities | Real Article 28 | MATCH |
| 29 | Application of a conformity assessment body for notification | Real Article 29 | MATCH |
| 30 | Notification procedure | Real Article 30 | MATCH |
| 31 | Requirements relating to notified bodies | Real Article 31 | MATCH |
| 32 | Subsidiaries of and subcontracting by notified bodies | Real Article 33 ("Subsidiaries of notified bodies and subcontracting") | **MISMATCH (title)** — real Article 32 is "Presumption of conformity with requirements relating to notified bodies", not covered anywhere in the DB under its correct number |
| 33 | Operational obligations of notified bodies | Real Article 34 | **MISMATCH (title)** |
| 34 | Identification numbers and lists of notified bodies | Real Article 35 | **MISMATCH (title)** |
| 35 | Changes to notifications | Real Article 36 | **MISMATCH (title)** |
| 36 | Challenge to the competence of notified bodies | Real Article 37 | **MISMATCH (title)** |
| 37 | Coordination of notified bodies | Real Article 38 | **MISMATCH (title)** |
| 38 | Conformity assessment bodies under the Cybersecurity Act | Not found verbatim at any single real article checked; closest is part of real Article 39's third-country language. Likely further drift | **MISMATCH** |
| 39 | Conformity assessment bodies in third countries | Real Article 39, content roughly matches but numbering one off from titles above | PARTIAL |

None of Articles 28–39 require any customer profile data (all regulator/notified-body process articles, correctly `profile_field: null`), so there is no data-gap impact from this drift — only a content-accuracy / customer-trust risk if these article numbers are ever surfaced to users (e.g. in a DPA-analysis citation or compliance report referencing "Article 32").

---

## Chapter III, Section 5 — Standards, Conformity, CE Marking, Registration (Articles 40–49)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 40 | Harmonised standards and standardisation deliverables | MATCH | None actionable (presumption-of-conformity mechanism) | N/A | No |
| 41 | Common specifications | MATCH | None actionable | N/A | No |
| 42 | Presumption of conformity with certain requirements | MATCH | None actionable | N/A | No |
| 43 | Conformity assessment | MATCH | Whether the high-risk system has undergone the required conformity-assessment procedure (self-assessment vs third-party, depending on Annex III category) | NO — no `conformity_assessment_status` field | YES (×2) |
| 44 | Certificates | MATCH | Whether a notified-body certificate exists and its expiry (max 5 years) | NO | YES (×2) |
| 45 | Extraordinary functioning of notified bodies (DB title: "Extraordinary functioning of notified bodies" — matches real Article 45 by title; content checked is informational) | MATCH | None actionable | N/A | No |
| 46 | Appeal against decisions of notified bodies — **title drift**: DB content is "Derogation from conformity assessment procedure" (real Article 46), but DB's title field says "Appeal against decisions of notified bodies" (real Article 46's actual title is "Derogation from conformity assessment procedure"; "Appeal" is real Article 46... wait — checked: real Article 46 title IS "Derogation from conformity assessment procedure", confirmed) | **MISMATCH (title only)** — DB title text doesn't match DB's own (correct) description content | Whether an emergency derogation from conformity assessment was used | NO | No |
| 47 | EU declaration of conformity | MATCH | Whether an EU declaration of conformity has been drawn up | NO | YES (`role`, `high_risk_categories`) |
| 48 | CE marking of conformity | MATCH | Whether CE marking has been affixed | NO | YES (`role`, `high_risk_categories`) |
| 49 | Registration | MATCH | Whether the system is registered in the EU database (Article 71) | NO | YES (`high_risk_categories`, `role`) |

---

## Chapter IV — Transparency for Certain AI Systems (Article 50)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 50 | Transparency obligations for certain AI systems | MATCH (accurately covers chatbot disclosure, synthetic-content watermarking, emotion-recognition/biometric-categorisation disclosure, deepfake labelling) | Whether the company uses chatbots, generates synthetic media, or uses emotion-recognition/biometric-categorisation systems that interact with natural persons | NO — `uses_chatbot`, `generates_synthetic_content`, `uses_emotion_recognition` referenced in `evaluation_logic` don't exist anywhere; only the generic `uses_ai` boolean exists | No (not a typo of a real field — a genuine gap of 3 new fields) |

---

## Chapter V — General-Purpose AI Models (Articles 51–56)

This block has the worst content drift in the whole regulation. Real Article 54 ("Authorised representatives of providers of GPAI models") appears to be skipped/omitted, shifting everything after it by one article number's worth of content.

| # | DB Title | Real content actually at | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|---|
| 51 | Classification of general-purpose AI models as models with systemic risk | Real Article 51 | MATCH | Whether the company's GPAI model exceeds the 10^25 FLOPs systemic-risk threshold | PARTIAL — `ai_act_data.uses_gpai` exists as a boolean but has no FLOPs/systemic-risk granularity | YES — `ai_act_data.gpai_model` |
| 52 | Obligations for providers of general-purpose AI models | Real Article 53 (real Article 52 is "Procedure" — Commission notification process, not covered at all under its correct number anywhere in the DB) | **MISMATCH** | Whether company is a GPAI model provider with technical documentation, downstream-provider info, copyright policy, training-data summary in place | NO | YES |
| 53 | Obligations for providers of general-purpose AI models with systemic risk | Real Article 55 (real Article 53's actual obligations content is what DB calls Article 52) | **MISMATCH** | Whether GPAI model has model evaluation/adversarial testing, systemic risk mitigation, incident reporting, cybersecurity measures | NO | YES |
| 54 | Codes of practice | Real Article 56 (real Article 54, "Authorised representatives of providers of GPAI models," is missing entirely from the DB under any article number) | **MISMATCH** | None actionable (voluntary compliance mechanism) | N/A | YES |
| 55 | Other measures in support of innovation for providers of GPAI models | Does not match any single real article checked directly; appears to be a paraphrase of AI Office support functions scattered across the real text, not a discrete Article 55 (which is actually "Obligations of providers of GPAI models with systemic risk") | **MISMATCH** | None actionable | N/A | No |
| 56 | Qualitative description of parameters relevant for classification | Real **Annex XIII** content (the FLOPs/parameter-count/benchmark criteria list referenced by Article 51), not real Article 56 ("Codes of practice") | **MISMATCH** | None actionable directly (informational criteria list) | N/A | No |

**Real Article 54 — "Authorised representatives of providers of GPAI models" — is entirely absent from the ComplianceKit database.** This is a genuine missing-article gap, not just a relabeling issue.

---

## Chapter VI — Innovation Support (Articles 57–63)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 57 | AI regulatory sandboxes | MATCH | None actionable (Member State infrastructure obligation) | N/A | No |
| 58 | Detailed arrangements for AI regulatory sandboxes | MATCH | None actionable | N/A | No |
| 59 | Further processing of personal data for developing certain AI systems in the public interest in the AI regulatory sandbox | MATCH | None actionable | N/A | No |
| 60 | Testing of high-risk AI systems in real world conditions outside AI regulatory sandboxes | MATCH | Whether company conducts real-world testing of high-risk AI outside a sandbox | NO | No |
| 61 | Measures for providers and deployers, in particular SMEs including start-ups | **MISMATCH (title/content)** — DB's Article 61 content actually matches real Article 62; real Article 61 is "Informed consent to participate in testing in real world conditions outside AI regulatory sandboxes," which is absent from the DB under its correct number | None actionable for the DB's stated content (Member State SME support duty); the missing real-61 topic would need consent-documentation tracking for real-world AI testing | NO (for missing real Art. 61) | No |
| 62 | Mechanism to report concerns about AI systems | **MISMATCH** — DB's content actually matches real Article 63 ("Derogations for specific operators" — microenterprise QMS simplification); real Article 62 ("Measures for providers and deployers, SMEs") is the content DB has mislabeled as "61" | Whether company is a microenterprise eligible for simplified QMS compliance under Article 63 | YES — `company_size` (loosely) | No |
| 63 | Derogations for specific operators | MATCH (content correctly matches real Article 63 despite the drift one row up duplicating this topic under "62") | Whether company qualifies as a microenterprise | YES — `company_size` | No |

---

## Chapter VII — Governance (Articles 64–70)

Real Articles 64–70 cover the AI Office and the European AI Board (EU-level governance bodies) — none of this is customer-actionable. The DB instead has Articles 64–70 describing market-surveillance/incident/penalty content that actually belongs to real Articles 74, 79, 80/81, and 73/69 respectively. This is the most severe content-substitution found in the audit: the DB articles in this range read as plausible regulatory content, but every single one is describing the wrong real article.

| # | DB Title | Real content actually at | Verdict |
|---|---|---|---|
| 64 | Access to data and documentation | Not matched to any single real article directly; closest real Article 64 is "AI Office" (an EU institution-creation article with no such "access to data" content) | **MISMATCH** |
| 65 | Market surveillance and control of AI systems in the Union market | Real Article 74 | **MISMATCH** |
| 66 | Procedure for dealing with AI systems presenting a risk at national level | Real Article 79 | **MISMATCH** |
| 67 | Procedure for dealing with compliant high-risk AI systems that present a risk | Real Article 82 | **MISMATCH** |
| 68 | Union safeguard procedure | Real Article 81 | **MISMATCH** |
| 69 | Reporting of serious incidents | Real Article 73 (real Article 69 is "Access to the pool of experts by the Member States") | **MISMATCH** |
| 70 | National competent authorities | Real Article 70 ("Designation of national competent authorities and single points of contact") — this one's title is a reasonable paraphrase and content roughly aligns | PARTIAL |

Data point implications: Article 64 ("Access to data and documentation," DB profile_field `ai_act_data.high_risk_categories`) and Article 69 ("Reporting of serious incidents," same dangling field) are both customer-facing in the DB's framing — but since their actual legal content doesn't correspond to what's titled, any remediation advice ComplianceKit generates from these rows is not legally grounded in the article it cites.

---

## Chapter VIII — EU Database (Article 71)

| # | Title | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|
| 71 | EU database for high-risk AI systems | MATCH (content correctly matches real Article 71) | Whether the high-risk AI system is registered in the EU database | NO | YES (×3, incl. both `high_risk_categories` and `role`) |

---

## Chapter IX — Post-Market Monitoring, Information Sharing, Market Surveillance (Articles 72–85)

| # | DB Title | Real content actually at | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|---|
| 72 | Post-market monitoring by providers and post-market monitoring plan for high-risk AI systems | Real Article 72 | MATCH | Whether a post-market monitoring plan exists | NO | YES |
| 73 | Reporting of serious incidents by providers of high-risk AI systems | Real Article 73 (title slightly expanded vs real "Reporting of serious incidents" but content matches) | MATCH | Whether a serious-incident reporting process exists | NO | YES |
| 74 | Market surveillance activities | Real Article 74 (content roughly matches, title compressed) | PARTIAL | None directly actionable | N/A | No |
| 75 | Mutual assistance, market surveillance activities and investigations of AI systems involving authorities from multiple Member States | Real Article 75 ("Mutual assistance, market surveillance and control of general-purpose AI systems") — close paraphrase | MATCH | None actionable | N/A | No |
| 76 | Oversight of testing in real world conditions | Real Article 76 ("Supervision of testing in real world conditions by market surveillance authorities") | MATCH | None actionable | N/A | No |
| 77 | Obligations of deployers | Real Article 77 is actually "Powers of authorities protecting fundamental rights" — completely different subject. DB's "Article 77" content is a duplicate/restatement of deployer obligations already covered correctly at Article 26 | **MISMATCH** | (duplicate of Article 26's data needs) | PARTIAL (role exists conceptually) | YES (×2) |
| 78 | Confidentiality | Real Article 78 | MATCH | None actionable | N/A | No |
| 79 | Penalties | Real Article 79 is actually "Procedure at national level for dealing with AI systems presenting a risk" — Article 79 is not about penalties at all; the real penalties article is 99 | **MISMATCH** | None actionable for DB's stated content | N/A | No |
| 80 | Penalties for providers of general-purpose AI models | Real Article 80 is "Procedure for dealing with AI systems classified by the provider as non-high-risk in application of Annex III" — not about GPAI penalties (those are real Article 101) | **MISMATCH** | Whether GPAI model presents systemic risk (DB's stated topic) | PARTIAL (`uses_gpai` exists, no systemic-risk granularity) | YES — `gpai_model` |
| 81 | Procedural rules for the adoption of supervisory measures by the AI Office | Real Article 81 is "Union safeguard procedure" | **MISMATCH** | None actionable | N/A | No |
| 82 | Right to be heard and access to the file | Real Article 82 is "Compliant AI systems which present a risk" | **MISMATCH** | None actionable | N/A | No |
| 83 | Limitation periods for the imposition of penalties | Real Article 83 is "Formal non-compliance" | **MISMATCH** | None actionable | N/A | No |
| 84 | Publication of decisions | Real Article 84 is "Union AI testing support structures" | **MISMATCH** | None actionable | N/A | No |
| 85 | European AI Office | Real Article 85 is "Right to lodge a complaint with a market surveillance authority" — a customer/data-subject right, not an EU-institution article | **MISMATCH** | Whether company has a process for handling AI-related complaints from affected persons | NO | No |

---

## Chapter X — Delegated Powers and Committee Procedure / Confidentiality and Individual Rights (Articles 86–98)

| # | DB Title | Real content actually at | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|---|
| 86 | Right to explanation | Real Article 86 ("Right to explanation of individual decision-making") — **this one is correctly aligned** | MATCH | Whether the company has a process to provide affected persons with explanations of high-risk AI decisions | NO | YES (`high_risk_categories`, `role`) |
| 87 | Reporting of breaches and protection of reporting persons | Real Article 87 ("Reporting of infringements and protection of reporting persons") — correctly aligned, close paraphrase | MATCH | None actionable (whistleblower-protection duty) | N/A | No |
| 88 | AI systems and GPAI models for general security purposes | Real Article 88 is "Enforcement of the obligations of providers of general-purpose AI models" — unrelated subject | **MISMATCH** | None actionable for DB's stated topic (military/security AI exemption is actually covered under Article 2(3), not 88) | N/A | No |
| 89 | AI systems with specific transparency obligations | Real Article 89 is "Monitoring actions" (AI Office monitoring powers) — unrelated; transparency obligations are Article 50, already covered | **MISMATCH** | (duplicate of Article 50 topic) | N/A | No |
| 90 | European Artificial Intelligence Board | Real Article 90 is "Alerts of systemic risks by the scientific panel" — Board creation is actually real Article 65 | **MISMATCH** | None actionable | N/A | No |
| 91 | Tasks of the AI Board | Real Article 91 is "Power to request documentation and information" (AI Office enforcement power over GPAI providers) | **MISMATCH** | Whether company can respond to AI Office documentation requests for its GPAI model | N/A | No |
| 92 | Scientific panel of independent experts | Real Article 92 is "Power to conduct evaluations" | **MISMATCH** | None actionable | N/A | No |
| 93 | Advisory forum | Real Article 93 is "Power to request measures" | **MISMATCH** | None actionable | N/A | No |
| 94 | Involvement of the Advisory Forum in the functioning of the Board | Real Article 94 is "Procedural rights of economic operators of the general-purpose AI model" | **MISMATCH** | Whether company (as a GPAI provider) has been given due-process rights before AI Office sanctions | N/A | No |
| 95 | Codes of conduct for voluntary application of specific requirements | Real Article 95 — correctly aligned | MATCH | None actionable (voluntary scheme) | N/A | No |
| 96 | Guidelines from the Commission on the implementation of this Regulation | Real Article 96 — correctly aligned | MATCH | None actionable | N/A | No |
| 97 | Exercise of the delegation | Real Article 97 — correctly aligned | MATCH | None actionable | N/A | No |
| 98 | Committee procedure | Real Article 98 — correctly aligned | MATCH | None actionable | N/A | No |

Note: Articles 95–98 realign correctly after the 88–94 drift zone, suggesting the drift in 88–94 is an isolated insertion/deletion error rather than a a running offset for the rest of the document.

---

## Chapter XI/XII — Penalties and Final/Transitional Provisions (Articles 99–113)

This is the second-most severe content-substitution zone: the **penalties article itself (real Article 99, EUR 35M/7% fines for Article 5 violations) is mislabeled in the DB as "Amendments to Regulation (EU) No 300/2008"** — an unrelated aviation-security legislative amendment. Everything from 99–112 is shifted by a consistent **+3 offset** (DB article N actually contains real article N+3's content), until Article 113 which is correct again (entry into force, identical at both ends of the document).

| # | DB Title | Real content actually at | Verdict | Data point needed | Exists? | Dangling ref? |
|---|---|---|---|---|---|---|
| 99 | Amendments to Regulation (EU) No 300/2008 | Real Article 102 | **MISMATCH** — real Article 99 is "Penalties" (the core fines article: EUR 35M/7% for Art. 5 violations, EUR 15M/3% for most other operator violations, EUR 7.5M/1% for misleading information to authorities) | None actionable directly, but this is the article that determines fine exposure for every other gap found elsewhere in this audit — its complete absence under the correct number is a significant content gap | N/A | No |
| 100 | Amendments to Regulation (EU) No 167/2013 | Real Article 103 | **MISMATCH** — real Article 100 is "Administrative fines on Union institutions, bodies, offices and agencies" | N/A | N/A | No |
| 101 | Amendments to Regulation (EU) No 168/2013 | Real Article 104 | **MISMATCH** — real Article 101 is "Fines for providers of general-purpose AI models" (up to EUR 15M/3% turnover) | None actionable directly, but this is the GPAI-specific fines article missing from the DB under its correct number | N/A | No |
| 102 | Amendments to Directive 2014/90/EU | Real Article 105 | **MISMATCH** — real Article 102 is "Amendment to Regulation (EC) No 300/2008" | N/A | N/A | No |
| 103 | Amendments to Directive (EU) 2016/797 | Real Article 106 | **MISMATCH** — real Article 103 is "Amendment to Regulation (EU) No 167/2013" | N/A | N/A | No |
| 104 | Amendments to Regulation (EU) 2018/858 | Real Article 107 | **MISMATCH** | N/A | N/A | No |
| 105 | Amendments to Regulation (EU) 2019/2144 | Real Article 108 | **MISMATCH** — real Article 105 is "Amendment to Directive 2014/90/EU" | N/A | N/A | No |
| 106 | Amendments to Regulation (EU) 2020/1056 | No matching real article found at any checked location (real Article 106 is "Amendment to Directive (EU) 2016/797"; "Regulation (EU) 2020/1056" does not appear among the 12 amended instruments in the real text at all) | **MISMATCH** — likely a fabricated/incorrect amended-instrument reference | N/A | N/A | No |
| 107 | Amendments to Regulation (EU) No 575/2013 | No matching real article found (real Article 107 is "Amendment to Regulation (EU) 2018/858"; "Regulation (EU) No 575/2013" — Capital Requirements Regulation — does not appear in the real amendments list) | **MISMATCH** — likely fabricated | N/A | N/A | No |
| 108 | Amendments to Directive 2013/36/EU | No matching real article found (real Article 108 is "Amendments to Regulation (EU) 2018/1139"; "Directive 2013/36/EU" — CRD IV — is not in the real amendments list) | **MISMATCH** — likely fabricated | N/A | N/A | No |
| 109 | AI systems already placed on the market or put into service | Real Article 109 is "Amendment to Regulation (EU) 2019/2144" | **MISMATCH** — DB title for 109 actually correctly describes the *topic* of real Article 111, just three articles early | N/A | N/A | No |
| 110 | Evaluation and review | Real Article 110 is "Amendment to Directive (EU) 2020/1828" | **MISMATCH** — DB title actually correctly describes real Article 112's topic | N/A | N/A | No |
| 111 | Repeal | Real Article 111 is "AI systems already placed on the market or put into service and general-purpose AI models already placed on the market" — there is **no standalone "Repeal" article** in the real Regulation at all (this Act doesn't repeal a predecessor act; it's a new regulation) | **MISMATCH** — fabricated article topic | N/A | N/A | No |
| 112 | Transitional provisions | Real Article 112 is "Evaluation and review" | **MISMATCH** | N/A | N/A | No |
| 113 | Entry into force and application | Real Article 113 — **correctly aligned** | MATCH | None actionable | N/A | No |

None of Articles 99–112 carry a `profile_field`, so there's no functional/runtime impact on the assessment engine from this drift, but the content is materially wrong if ever surfaced to a customer (most importantly, Article 99's real content — the fines/penalties regime — is completely missing from the database under its correct, and most-likely-to-be-cited, article number).

---

## Recommendations

1. **Immediate (data-integrity bug, affects assessment engine):** Fix the three typo'd field references (`high_risk_categories` → `high_risk_ai_categories`, `role` → `ai_role`, `gpai_model` → `uses_gpai`) across all 38 affected articles. Verify whether `services/policy-engine/app/engine/applicability.py` / `scorer.py` already remap these names — if not, every high-risk and GPAI rule is currently unevaluable in the live assessment pipeline.
2. **High priority (content-integrity, customer trust):** Re-derive and replace the title+description+plain_english for the 44 mismatched articles directly from the official Regulation (EU) 2024/1689 text, focused first on Article 99 (Penalties — the most consequential one to get right) and the GPAI block (51–56, including the entirely-missing real Article 54).
3. **Product gap (real, not a bug):** Add profile fields to capture the substantive Article 9–15, 17–19, 43–44, 47–49, 71, 72–73, 86 controls (risk management system, data governance docs, technical documentation, logging, QMS, conformity assessment status, EU database registration, post-market monitoring plan, explanation-to-affected-persons process) — currently only the high-risk-category trigger exists, with no way to record whether the actual control is in place.
4. **Product gap:** Add the missing Article 27 fields (`is_public_body`, `provides_public_service`) and Article 50 fields (chatbot/synthetic-content/emotion-recognition flags) if these articles are meant to be evaluable rather than purely informational.
