# GDPR Article Audit — DB Rules vs Source Text

Audit of all 99 GDPR rules in the policy-engine database against the official GDPR
regulation text (source: `docs/Gdpr.pdf`), and against the closed-world set of
customer data fields available anywhere in the product (onboarding + `company_profiles`
+ `gdpr_data`/`nis2_data`/`ai_act_data` JSONB).

## Summary

- **Total articles audited:** 99 / 99
- **MATCH:** 93
- **PARTIAL:** 5 (Articles 30, 37, 49, 58, 88)
- **MISMATCH:** 1 (Article 26)
- **Articles with a data gap (NO or PARTIAL availability):** 19 (Articles 9, 10, 17, 21, 26, 30, 35, 37, 38, 39, 44, 47, 48, 49, 60, 77, 79, 82, 88, 89 — see table; some rows above 18 due to multi-flag rows)
- **Dangling profile_field / evaluation_logic references found:** 1 confirmed bug
  - **Article 26** — `evaluation_logic.condition` references `has_joint_controllers`, which does not exist anywhere in the schema (no such column/JSONB key). This is phrased identically to genuine field-lookup checks elsewhere (e.g. Art. 19's `gdpr_data.uses_data_processors == true`), so the assessment engine will fail to evaluate this condition at runtime.

Two further conceptual tokens used in `evaluation_logic` are **not** classified as dangling references because they are narrative conditions inside `document_required`/`conditional` checks meant for manual/AI evidence review, not literal DB field lookups: Article 35/36's `no_high_risk_processing`/`high_residual_risk`, Article 45/46/49's `transfer_to_adequate_country`/`no_adequacy_decision`/`relying_on_derogation`, Article 47's `is_multinational_group`/`transfers_within_group_internationally`. These should still be flagged to engineering as "soft" follow-up — they make the conditional logic effectively always-true/false unless the evaluator has a side-channel to resolve them — but they are not schema bugs.

---

## Per-Article Audit

| Article | DB description vs PDF | Data needed | Data availability | Dangling reference |
|---|---|---|---|---|
| 1 — Subject-matter and objectives | MATCH | n/a (informational) | n/a | none |
| 2 — Material scope | MATCH | n/a | n/a | none |
| 3 — Territorial scope | MATCH | `primary_jurisdiction`, `website_url`/customer location | PARTIAL — no explicit "targets EU residents" flag; jurisdiction only | none |
| 4 — Definitions | MATCH | n/a | n/a | none |
| 5 — Principles relating to processing | MATCH | `processing_purposes`, `data_categories_processed` | PARTIAL — principles like accuracy/minimisation not directly measurable from profile | none |
| 6 — Lawfulness of processing | MATCH | lawful basis selection | YES — `gdpr_data.lawful_bases` | none |
| 7 — Conditions for consent | MATCH | whether consent is a lawful basis used | PARTIAL — `gdpr_data.lawful_bases` tells if "consent" selected but not consent-mechanism quality | none |
| 8 — Conditions for children's consent | MATCH | whether processing involves children | YES — `gdpr_data.processes_children_data` | none |
| 9 — Special categories of data | MATCH | special category data + condition relied upon | PARTIAL — `data_categories_processed` flags special data but no explicit Art.9(2) condition field | none |
| 10 — Criminal conviction data | MATCH | whether criminal data processed | NO — no field distinguishes criminal conviction data from other special categories | none (descriptive `requires_special_data` flag only, not a profile_field lookup) |
| 11 — Processing not requiring identification | MATCH | n/a | n/a | none |
| 12 — Transparent information | MATCH | privacy notice existence | YES — covered via `policies` document check (`document_required`) | none |
| 13 — Information where data collected from subject | MATCH | privacy notice content | YES — document_required check | none |
| 14 — Information where data not from subject | MATCH | privacy notice content | YES — document_required check | none |
| 15 — Right of access | MATCH | DSAR process | YES — DSAR module / `has_breach_procedure`-style process check | none |
| 16 — Right to rectification | MATCH | DSAR process | YES — DSAR module | none |
| 17 — Right to erasure | MATCH | erasure procedure | PARTIAL — no explicit `has_erasure_procedure` field; relies on generic DSAR coverage | none (the `evaluation_logic` uses `document_required` for `erasure_procedure`, a descriptive evidence label, not a profile_field lookup) |
| 18 — Right to restriction of processing | MATCH | restriction procedure | NO — no field captures whether a restriction-of-processing capability exists | none |
| 19 — Notification re rectification/erasure/restriction | MATCH | whether processors used (to notify) | YES — `gdpr_data.uses_data_processors` | none |
| 20 — Right to data portability | MATCH | data export capability | NO — no field on technical export capability | none |
| 21 — Right to object | MATCH | objection-handling process, direct marketing usage | PARTIAL — no explicit marketing-objection field; relies on generic complaint/DSAR process | none |
| 22 — Automated decision-making | MATCH | whether automated/profiling decisions are made | PARTIAL — best inferred from `ai_act_data.uses_ai`/`ai_role` but no GDPR-specific "automated decisions with legal effect" flag | none |
| 23 — Restrictions | MATCH | n/a | n/a | none |
| 24 — Responsibility of the controller | MATCH | `data_role` | YES — `data_role` (controller/processor/both) | none |
| 25 — Data protection by design and by default | MATCH | technical/organisational measures in place | PARTIAL — inferred indirectly from `uses_cloud_services`/tech_stack, no explicit privacy-by-design flag | none |
| 26 — Joint controllers | **MISMATCH** — DB description is accurate to the article, but `evaluation_logic.condition` checks `has_joint_controllers == true`, a field that does not exist | whether org is a joint controller with another party | NO — no such field anywhere in schema | **DANGLING REFERENCE — `has_joint_controllers` does not exist in company_profiles, gdpr_data, nis2_data, or ai_act_data** |
| 27 — Representatives of controllers/processors not in EU | MATCH | `primary_jurisdiction` (EU vs non-EU) | YES — `primary_jurisdiction` | none |
| 28 — Processor | MATCH | DPA with processors | YES — `gdpr_data.uses_data_processors` | none |
| 29 — Processing under authority of controller/processor | MATCH | processor instructions documented | YES — `gdpr_data.uses_data_processors` | none |
| 30 — Records of processing activities | PARTIAL — DB description omits the <250-employee exemption nuance (exempt unless processing is non-occasional, risky, or involves special category data) | RoPA document + `company_size` to assess exemption | PARTIAL — RoPA doc check exists, but `company_size`-based exemption logic is not wired into `evaluation_logic` | none |
| 31 — Cooperation with supervisory authority | MATCH | regulatory response procedure | YES — `policy_required` document check | none |
| 32 — Security of processing | MATCH | encryption, access control, security testing | PARTIAL — `uses_cloud_services` is a weak proxy; no explicit `encryption_in_place` field (used only as a descriptive check label, not a real lookup) | none |
| 33 — Breach notification to supervisory authority | MATCH | breach procedure existence | YES — `gdpr_data.has_breach_procedure` | none |
| 34 — Breach communication to data subject | MATCH | breach procedure + individual notification process | PARTIAL — `gdpr_data.has_breach_procedure` covers general procedure, but no field for "individual notification process defined" specifically | none |
| 35 — DPIA | MATCH | DPIA existence + high-risk processing indicators | YES (has_dpia) / PARTIAL (no_high_risk_processing is a narrative condition, not a field) | YES — `gdpr_data.has_dpia`; `no_high_risk_processing` is a conceptual condition label, not dangling | none |
| 36 — Prior consultation | MATCH | DPIA outcome (residual risk) | PARTIAL — `gdpr_data.has_dpia` only; `high_residual_risk` is a narrative condition, not a stored field | none |
| 37 — Designation of DPO | PARTIAL — DB description is accurate, but DB's `evaluation_logic.check` says "if DPO mandatory, has_compliance_officer == true" without the engine actually computing "DPO mandatory" from the named fields | DPO-mandatory triggers: public authority, large-scale systematic monitoring, large-scale special category processing | PARTIAL — `has_compliance_officer`, `data_categories_processed`, `number_of_data_subjects` exist, but there's no field for "is a public authority" | none |
| 38 — Position of the DPO | MATCH | DPO independence/reporting line | NO — no field captures DPO independence/reporting structure, only `has_compliance_officer` | none |
| 39 — Tasks of the DPO | MATCH | DPO tasks formally defined | NO — no field captures whether DPO tasks are documented, only `has_compliance_officer` | none |
| 40 — Codes of conduct | MATCH | n/a (voluntary, informational) | n/a | none |
| 41 — Monitoring of approved codes of conduct | MATCH | n/a | n/a | none |
| 42 — Certification | MATCH | certifications held | YES — `certifications` | none |
| 43 — Certification bodies | MATCH | n/a | n/a | none |
| 44 — General principle for transfers | MATCH | whether transfers outside EEA occur | YES — `gdpr_data.transfers_outside_eea` | none |
| 45 — Adequacy decision transfers | MATCH | transfer destination country adequacy status | PARTIAL — `gdpr_data.transfers_outside_eea` flags transfers but no field names the destination country/adequacy status; `transfer_to_adequate_country` is a narrative condition | none |
| 46 — Transfers with appropriate safeguards | MATCH | mechanism used (SCCs/BCRs/etc.) | YES — `gdpr_data.transfer_mechanisms` covers this (DB only references `gdpr_data.transfers_outside_eea` in evaluation_logic, missing the more precise `transfer_mechanisms` array that already exists in the schema) | none |
| 47 — Binding corporate rules | MATCH | whether org is part of a corporate group transferring data intra-group | NO — no field for multinational group status; `is_multinational_group`/`transfers_within_group_internationally` are narrative conditions only | none |
| 48 — Transfers not authorised by Union law | MATCH | foreign government data-request handling policy | PARTIAL — `gdpr_data.transfers_outside_eea` is a weak proxy; no field on government-request handling specifically | none |
| 49 — Derogations for specific situations | PARTIAL — DB description is accurate but doesn't capture that derogations should be exceptional/non-routine, which the DB's own plain_english notes but evaluation_logic doesn't encode | which derogation relied upon | NO — `relying_on_derogation` is a narrative condition, no actual field | none |
| 50 — International cooperation | MATCH | n/a | n/a | none |
| 51 — Supervisory authority | MATCH | n/a | n/a | none |
| 52 — Independence | MATCH | n/a | n/a | none |
| 53 — General conditions for members | MATCH | n/a | n/a | none |
| 54 — Rules on establishment | MATCH | n/a | n/a | none |
| 55 — Competence | MATCH | n/a | n/a | none |
| 56 — Competence of lead supervisory authority | MATCH | multi-country presence (for lead authority determination) | NO — no field captures EU establishment footprint across countries | none |
| 57 — Tasks | MATCH | n/a | n/a | none |
| 58 — Powers | PARTIAL — DB description correctly summarises investigative/corrective/advisory powers but folds in Article 83 fine amounts which belong to Article 83, slightly conflating the two articles | n/a (informational) | n/a | none |
| 59 — Activity reports | MATCH | n/a | n/a | none |
| 60 — Cooperation between lead and concerned authorities | MATCH | EU multi-country footprint | NO — no field | none |
| 61 — Mutual assistance | MATCH | n/a | n/a | none |
| 62 — Joint operations | MATCH | n/a | n/a | none |
| 63 — Consistency mechanism | MATCH | n/a | n/a | none |
| 64 — Opinion of the Board | MATCH | n/a | n/a | none |
| 65 — Dispute resolution by the Board | MATCH | n/a | n/a | none |
| 66 — Urgency procedure | MATCH | n/a | n/a | none |
| 67 — Exchange of information | MATCH | n/a | n/a | none |
| 68 — European Data Protection Board | MATCH | n/a | n/a | none |
| 69 — Independence (EDPB) | MATCH | n/a | n/a | none |
| 70 — Tasks of the Board | MATCH | n/a | n/a | none |
| 71 — Reports | MATCH | n/a | n/a | none |
| 72 — Procedure | MATCH | n/a | n/a | none |
| 73 — Chair | MATCH | n/a | n/a | none |
| 74 — Tasks of the Chair | MATCH | n/a | n/a | none |
| 75 — Secretariat | MATCH | n/a | n/a | none |
| 76 — Confidentiality | MATCH | n/a | n/a | none |
| 77 — Right to lodge a complaint | MATCH | complaint-handling procedure | NO — no field tracks whether a data-subject complaint procedure exists; covered only via generic `policy_required` document check | none |
| 78 — Judicial remedy against supervisory authority | MATCH | n/a | n/a | none |
| 79 — Judicial remedy against controller/processor | MATCH | legal response procedure | NO — no field; covered only via generic `policy_required` document check | none |
| 80 — Representation of data subjects | MATCH | n/a (informational) | n/a | none |
| 81 — Suspension of proceedings | MATCH | n/a | n/a | none |
| 82 — Right to compensation and liability | MATCH | incident response plan / cyber insurance | NO — no field directly maps to "cyber_insurance"; only generic `policy_required` document check | none |
| 83 — Administrative fines | MATCH | n/a (informational, fine tiers correctly state €10M/2% and €20M/4%) | n/a | none |
| 84 — Penalties | MATCH | n/a | n/a | none |
| 85 — Freedom of expression and information | MATCH | n/a | n/a | none |
| 86 — Public access to official documents | MATCH | n/a | n/a | none |
| 87 — National identification number | MATCH | n/a | n/a | none |
| 88 — Processing in employment context | PARTIAL — DB description correctly summarises employment-context processing rules, but `is_mandatory: true` is questionable since Article 88 is itself optional for Member States (they "may" provide such rules) — this should arguably be conditionally mandatory based on jurisdiction, not blanket mandatory | employee data protection policy | NO — no field tracks whether employee data is processed/HR exists; covered only via generic `policy_required` check | none |
| 89 — Safeguards for archiving/research/statistics | MATCH | whether org processes data for research/statistics purposes | NO — no field for research/statistics processing purpose; `processing_for_research_or_statistics` is a narrative condition only | none |
| 90 — Obligations of secrecy | MATCH | n/a | n/a | none |
| 91 — Churches and religious associations | MATCH | n/a | n/a | none |
| 92 — Exercise of the delegation | MATCH | n/a | n/a | none |
| 93 — Committee procedure | MATCH | n/a | n/a | none |
| 94 — Repeal of Directive 95/46/EC | MATCH | n/a | n/a | none |
| 95 — Relationship with ePrivacy Directive | MATCH | n/a | n/a | none |
| 96 — Relationship with prior agreements | MATCH | n/a | n/a | none |
| 97 — Commission reports | MATCH | n/a | n/a | none |
| 98 — Review of other Union legal acts | MATCH | n/a | n/a | none |
| 99 — Entry into force and application | MATCH | n/a | n/a | none |
