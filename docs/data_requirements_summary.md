# GDPR — Data Required vs Currently Available

| 1 — Subject-matter and objectives | n/a (informational) | n/a |
| 2 — Material scope | n/a | n/a |
| 3 — Territorial scope | `primary_jurisdiction`, `website_url`/customer location | PARTIAL — no explicit "targets EU residents" flag; jurisdiction only |
| 4 — Definitions | n/a | n/a |
| 5 — Principles relating to processing | `processing_purposes`, `data_categories_processed` | PARTIAL — principles like accuracy/minimisation not directly measurable from profile |
| 6 — Lawfulness of processing | lawful basis selection | YES — `gdpr_data.lawful_bases` |
| 7 — Conditions for consent | whether consent is a lawful basis used | PARTIAL — `gdpr_data.lawful_bases` tells if "consent" selected but not consent-mechanism quality |
| 8 — Conditions for children's consent | whether processing involves children | YES — `gdpr_data.processes_children_data` |
| 9 — Special categories of data | special category data + condition relied upon | PARTIAL — `data_categories_processed` flags special data but no explicit Art.9(2) condition field |
| 10 — Criminal conviction data | whether criminal data processed | NO — no field distinguishes criminal conviction data from other special categories |
| 11 — Processing not requiring identification | n/a | n/a |
| 12 — Transparent information | privacy notice existence | YES — covered via `policies` document check (`document_required`) |
| 13 — Information where data collected from subject | privacy notice content | YES — document_required check |
| 14 — Information where data not from subject | privacy notice content | YES — document_required check |
| 15 — Right of access | DSAR process | YES — DSAR module / `has_breach_procedure`-style process check |
| 16 — Right to rectification | DSAR process | YES — DSAR module |
| 17 — Right to erasure | erasure procedure | PARTIAL — no explicit `has_erasure_procedure` field; relies on generic DSAR coverage |
| 18 — Right to restriction of processing | restriction procedure | NO — no field captures whether a restriction-of-processing capability exists |
| 19 — Notification re rectification/erasure/restriction | whether processors used (to notify) | YES — `gdpr_data.uses_data_processors` |
| 20 — Right to data portability | data export capability | NO — no field on technical export capability |
| 21 — Right to object | objection-handling process, direct marketing usage | PARTIAL — no explicit marketing-objection field; relies on generic complaint/DSAR process |
| 22 — Automated decision-making | whether automated/profiling decisions are made | PARTIAL — best inferred from `ai_act_data.uses_ai`/`ai_role` but no GDPR-specific "automated decisions with legal effect" flag |
| 23 — Restrictions | n/a | n/a |
| 24 — Responsibility of the controller | `data_role` | YES — `data_role` (controller/processor/both) |
| 25 — Data protection by design and by default | technical/organisational measures in place | PARTIAL — inferred indirectly from `uses_cloud_services`/tech_stack, no explicit privacy-by-design flag |
| 26 — Joint controllers | whether org is a joint controller with another party | NO — no such field anywhere in schema |
| 27 — Representatives of controllers/processors not in EU | `primary_jurisdiction` (EU vs non-EU) | YES — `primary_jurisdiction` |
| 28 — Processor | DPA with processors | YES — `gdpr_data.uses_data_processors` |
| 29 — Processing under authority of controller/processor | processor instructions documented | YES — `gdpr_data.uses_data_processors` |
| 30 — Records of processing activities | RoPA document + `company_size` to assess exemption | PARTIAL — RoPA doc check exists, but `company_size`-based exemption logic is not wired into `evaluation_logic` |
| 31 — Cooperation with supervisory authority | regulatory response procedure | YES — `policy_required` document check |
| 32 — Security of processing | encryption, access control, security testing | PARTIAL — `uses_cloud_services` is a weak proxy; no explicit `encryption_in_place` field (used only as a descriptive check label, not a real lookup) |
| 33 — Breach notification to supervisory authority | breach procedure existence | YES — `gdpr_data.has_breach_procedure` |
| 34 — Breach communication to data subject | breach procedure + individual notification process | PARTIAL — `gdpr_data.has_breach_procedure` covers general procedure, but no field for "individual notification process defined" specifically |
| 35 — DPIA | DPIA existence + high-risk processing indicators | YES (has_dpia) / PARTIAL (no_high_risk_processing is a narrative condition, not a field) |
| 36 — Prior consultation | DPIA outcome (residual risk) | PARTIAL — `gdpr_data.has_dpia` only; `high_residual_risk` is a narrative condition, not a stored field |
| 37 — Designation of DPO | DPO-mandatory triggers: public authority, large-scale systematic monitoring, large-scale special category processing | PARTIAL — `has_compliance_officer`, `data_categories_processed`, `number_of_data_subjects` exist, but there's no field for "is a public authority" |
| 38 — Position of the DPO | DPO independence/reporting line | NO — no field captures DPO independence/reporting structure, only `has_compliance_officer` |
| 39 — Tasks of the DPO | DPO tasks formally defined | NO — no field captures whether DPO tasks are documented, only `has_compliance_officer` |
| 40 — Codes of conduct | n/a (voluntary, informational) | n/a |
| 41 — Monitoring of approved codes of conduct | n/a | n/a |
| 42 — Certification | certifications held | YES — `certifications` |
| 43 — Certification bodies | n/a | n/a |
| 44 — General principle for transfers | whether transfers outside EEA occur | YES — `gdpr_data.transfers_outside_eea` |
| 45 — Adequacy decision transfers | transfer destination country adequacy status | PARTIAL — `gdpr_data.transfers_outside_eea` flags transfers but no field names the destination country/adequacy status; `transfer_to_adequate_country` is a narrative condition |
| 46 — Transfers with appropriate safeguards | mechanism used (SCCs/BCRs/etc.) | YES — `gdpr_data.transfer_mechanisms` covers this (DB only references `gdpr_data.transfers_outside_eea` in evaluation_logic, missing the more precise `transfer_mechanisms` array that already exists in the schema) |
| 47 — Binding corporate rules | whether org is part of a corporate group transferring data intra-group | NO — no field for multinational group status; `is_multinational_group`/`transfers_within_group_internationally` are narrative conditions only |
| 48 — Transfers not authorised by Union law | foreign government data-request handling policy | PARTIAL — `gdpr_data.transfers_outside_eea` is a weak proxy; no field on government-request handling specifically |
| 49 — Derogations for specific situations | which derogation relied upon | NO — `relying_on_derogation` is a narrative condition, no actual field |
| 50 — International cooperation | n/a | n/a |
| 51 — Supervisory authority | n/a | n/a |
| 52 — Independence | n/a | n/a |
| 53 — General conditions for members | n/a | n/a |
| 54 — Rules on establishment | n/a | n/a |
| 55 — Competence | n/a | n/a |
| 56 — Competence of lead supervisory authority | multi-country presence (for lead authority determination) | NO — no field captures EU establishment footprint across countries |
| 57 — Tasks | n/a | n/a |
| 58 — Powers | n/a (informational) | n/a |
| 59 — Activity reports | n/a | n/a |
| 60 — Cooperation between lead and concerned authorities | EU multi-country footprint | NO — no field |
| 61 — Mutual assistance | n/a | n/a |
| 62 — Joint operations | n/a | n/a |
| 63 — Consistency mechanism | n/a | n/a |
| 64 — Opinion of the Board | n/a | n/a |
| 65 — Dispute resolution by the Board | n/a | n/a |
| 66 — Urgency procedure | n/a | n/a |
| 67 — Exchange of information | n/a | n/a |
| 68 — European Data Protection Board | n/a | n/a |
| 69 — Independence (EDPB) | n/a | n/a |
| 70 — Tasks of the Board | n/a | n/a |
| 71 — Reports | n/a | n/a |
| 72 — Procedure | n/a | n/a |
| 73 — Chair | n/a | n/a |
| 74 — Tasks of the Chair | n/a | n/a |
| 75 — Secretariat | n/a | n/a |
| 76 — Confidentiality | n/a | n/a |
| 77 — Right to lodge a complaint | complaint-handling procedure | NO — no field tracks whether a data-subject complaint procedure exists; covered only via generic `policy_required` document check |
| 78 — Judicial remedy against supervisory authority | n/a | n/a |
| 79 — Judicial remedy against controller/processor | legal response procedure | NO — no field; covered only via generic `policy_required` document check |
| 80 — Representation of data subjects | n/a (informational) | n/a |
| 81 — Suspension of proceedings | n/a | n/a |
| 82 — Right to compensation and liability | incident response plan / cyber insurance | NO — no field directly maps to "cyber_insurance"; only generic `policy_required` document check |
| 83 — Administrative fines | n/a (informational, fine tiers correctly state €10M/2% and €20M/4%) | n/a |
| 84 — Penalties | n/a | n/a |
| 85 — Freedom of expression and information | n/a | n/a |
| 86 — Public access to official documents | n/a | n/a |
| 87 — National identification number | n/a | n/a |
| 88 — Processing in employment context | employee data protection policy | NO — no field tracks whether employee data is processed/HR exists; covered only via generic `policy_required` check |
| 89 — Safeguards for archiving/research/statistics | whether org processes data for research/statistics purposes | NO — no field for research/statistics processing purpose; `processing_for_research_or_statistics` is a narrative condition only |
| 90 — Obligations of secrecy | n/a | n/a |
| 91 — Churches and religious associations | n/a | n/a |
| 92 — Exercise of the delegation | n/a | n/a |
| 93 — Committee procedure | n/a | n/a |
| 94 — Repeal of Directive 95/46/EC | n/a | n/a |
| 95 — Relationship with ePrivacy Directive | n/a | n/a |
| 96 — Relationship with prior agreements | n/a | n/a |
| 97 — Commission reports | n/a | n/a |
| 98 — Review of other Union legal acts | n/a | n/a |
| 99 — Entry into force and application | n/a | n/a |

# NIS2 — Data Required vs Currently Available

| DB1 — Subject matter | None — informational article. | N/A (informational). |
| DB2 — Scope | Sector classification + entity size/turnover. | PARTIAL — sector is collected, size threshold is not separately modeled. |
| DB3 — Essential and important entities | Entity type classification (essential/important). | YES — `nis2_data.entity_type`. |
| DB4 — Sector-specific Union legal acts | Industry/sector. | YES — `company_profiles.industry`. |
| DB5 — National cybersecurity strategy | None — describes Member State, not tenant, obligations. | N/A. |
| DB6 — (title per DB: vulnerability-disclosure adjacent content) | Whether a coordinated vulnerability disclosure policy/process exists. | NO — GAP, not collected anywhere in the field list. |
| DB7 — National cyber crisis management framework | None — Member State obligation. | N/A. |
| DB8 — Competent authorities and single point of contact | None — Member State obligation. | N/A. |
| DB9 — CSIRTs | None — Member State obligation. | N/A. |
| DB10 — Requirements for CSIRTs | None — Member State obligation. | N/A. |
| DB11 — Coordinated vulnerability disclosure | Whether the org follows a coordinated/responsible vulnerability disclosure process. | NO — GAP, not collected. |
| DB12 — Cyber crisis management (EU-CyCLONe per DB) | None — EU/Member State institutional obligation. | N/A. |
| DB13 — Cooperation at Union level | None — institutional obligation. | N/A. |
| DB14 — CSIRTs network | None. | N/A. |
| DB15 — NIS Cooperation Group | None. | N/A. |
| DB16 — International cooperation | None. | N/A. |
| DB17 — Peer reviews | None. | N/A. |
| DB18 — Reporting obligations (incidents) | Whether an incident response/reporting process exists. | PARTIAL — `nis2_data.has_incident_response_plan` exists but only as a yes/no flag, not deadline-tracking detail. |
| DB19 — Use of European cybersecurity certification schemes | Whether the org uses any certified products/services. | NO — GAP, not collected. |
| DB20 — Governance | Whether management has approved a cybersecurity governance policy and undergone training. | NO — GAP, not collected (no governance-approval or board-training field exists). |
| DB21 — Cybersecurity risk-management measures | Presence of each of the 10 specific technical/organisational measures. | NO — GAP. None of `risk_analysis_policy`, `incident_handling_procedure`, `business_continuity_plan`, `supply_chain_security_policy`, `secure_development_policy`, `security_effectiveness_assessment`, `cyber_hygiene_training`, `cryptography_policy`, `access_control_policy` exist as collected fields. Only `nis2_data.has_mfa` (partially covers the MFA sub-measure) and `nis2_data.has_business_continuity_plan` exist among the ten. |
| DB22 — Coordinated risk assessments of critical supply chains | None — EU/Member State-level coordinated assessment, not tenant-level. | N/A. |
| DB23 — Reporting obligations | Whether an incident reporting/response process and timeline exist. | PARTIAL — `nis2_data.has_incident_response_plan` covers existence, not deadline-tracking capability. |
| DB24 — Technical guidelines and methodological guidelines on incident reporting | None — ENISA/Commission obligation, not tenant-level. | N/A. |
| DB25 — Notification to recipients of services and to the public | Whether a customer/public incident-notification procedure exists. | PARTIAL — closest field is `nis2_data.has_incident_response_plan`, but it does not specifically capture customer-notification capability. |
| DB26 — Jurisdiction and territoriality | Primary jurisdiction / where main establishment is located. | YES — `company_profiles.primary_jurisdiction`. |
| DB27 — Register of entities | Sector classification (to determine if the narrower Art 27 registration duty applies) plus registration completion status. | PARTIAL — sector is collected (with a dangling field name issue, see below); no field tracks actual registration completion. |
| DB28 — Database of domain name registration data | None — applies only to TLD registries/domain registration entities, an EU-level database obligation. | N/A. |
| DB29 — Cybersecurity information sharing arrangements | Whether the org participates in any information-sharing arrangement. | NO — GAP, not collected. |
| DB30 — Voluntary notification of relevant information | None — describes a voluntary right, not a measurable compliance state. | N/A. |
| DB31 — General aspects of supervision and enforcement | Entity type (essential vs important) to determine which supervisory regime applies. | YES — `nis2_data.entity_type`. |
| DB32 — Supervisory and enforcement measures re: essential entities | Entity type. | YES — `nis2_data.entity_type`. |
| DB33 — Supervisory and enforcement measures re: important entities | Entity type. | YES — `nis2_data.entity_type`. |
| DB34 — General rules on administrative fines | Entity type + global turnover (for fine exposure estimation). | PARTIAL — `nis2_data.entity_type` exists; no turnover/revenue field exists in the provided list. |
| DB35 — Infringements entailing a personal data breach | None — describes inter-authority cooperation, not a tenant-level fact. | N/A. |
| DB36 — Penalties | None — Member State obligation. | N/A. |
| DB37 — Mutual assistance | None — inter-authority obligation. | N/A. |
| DB38 — Joint supervisory actions | None — inter-authority obligation. | N/A. |
| DB39 — Exercise of the delegation | None. | N/A. |
| DB40 — Committee procedure | None. | N/A. |
| DB41 — Review | None. | N/A. |
| DB42 — Amendments to Regulation (EU) No 910/2014 | None. | N/A. |
| DB43 — Amendments to Directive (EU) 2018/1972 | None. | N/A. |
| DB44 — Repeal | None. | N/A. |
| DB45 — Transposition | None. | N/A. |
| DB46 — Entry into force | None. | N/A. |

# AI Act — Data Required vs Currently Available

| Article 1 — Subject matter | None (informational/scope statement) | N/A |
| Article 2 — Scope | Whether the company builds/sells/deploys AI in the EU or whose AI output affects EU persons | YES — `ai_act_data.uses_ai` |
| Article 3 — Definitions | None (informational) | N/A |
| Article 4 — AI literacy | Whether an AI-literacy training programme exists for staff/contractors using AI | NO — no `has_ai_literacy_training` field; only `ai_act_data.has_ai_governance_policy` exists and is not the same thing |
| Article 5 — Prohibited AI practices | Description accurately lists all 8 prohibited practice categories (manipulation, vulnerability exploitation, social scoring, predictive policing, facial-scraping databases, workplace/school emotion recognition, sensitive biometric categorisation, real-time public biometric ID for law enforcement). Needed data: whether the company engages in any of these 8 specific practices | PARTIAL — only `uses_ai` boolean exists; no per-practice flags. The 8 `prohibited_practices` keys named in `evaluation_logic` (`social_scoring`, `real_time_biometric_public`, etc.) are gaps, not real fields |
| Article 6 — Classification rules for high-risk AI systems | Whether the AI system falls into one of the 8 Annex III high-risk categories | YES (categories) — `ai_act_data.high_risk_ai_categories`, but DB references the wrong key name |
| Article 7 — Amendments to Annex III | None (informational — Commission's delegated-act power) | N/A |
| Article 8 — Compliance with the requirements | Whether company has any high-risk AI system (gates Articles 9-15 applicability) | YES (intended) |
| Article 9 — Risk management system | Whether a documented, lifecycle-wide AI risk management system exists | NO — no `has_ai_risk_management_system` field |
| Article 10 — Data and data governance | Whether training-data governance documentation (bias, representativeness, provenance) exists | NO — no equivalent field |
| Article 11 — Technical documentation | Whether Annex IV technical documentation exists for the high-risk system | NO |
| Article 12 — Record-keeping | Whether the AI system has automatic event/usage logging built in | NO |
| Article 13 — Transparency and provision of information to deployers | Whether instructions-for-use documentation (capabilities, limitations, risks) exists | NO |
| Article 14 — Human oversight | Whether human-oversight mechanisms (override/stop) are implemented | NO |
| Article 15 — Accuracy, robustness and cybersecurity | Whether the AI system has been tested for accuracy/robustness/adversarial-attack resilience | NO |
| Article 16 — Obligations of providers of high-risk AI systems | Whether company is a "provider" of high-risk AI (role + conformity/CE/registration status) | PARTIAL — role exists conceptually but wrong key referenced; no field for conformity/CE/registration status |
| Article 17 — Quality management system | Whether an ISO-9001-style QMS exists for high-risk AI development | NO |
| Article 18 — Documentation keeping | Whether technical/QMS documentation is retained for 10 years | NO |
| Article 19 — Automatically generated logs | Whether log retention period/policy exists | NO |
| Article 20 — Corrective actions and duty of information | Whether a corrective-action/recall process exists for non-conforming AI | NO |
| Article 21 — Cooperation with competent authorities | None actionable for a customer profile (regulator-facing duty) | N/A |
| Article 22 — Authorised representatives of providers not established in the Union | Whether company is a non-EU provider needing an EU authorised representative | YES — `primary_jurisdiction` (correct, not dangling) |
| Article 23 — Obligations of importers | Whether company is an importer of high-risk AI systems | PARTIAL (`role` concept exists, wrong key) |
| Article 24 — Obligations of distributors — **title note:** DB titles this "Obligations of product manufacturers"; real Article 24 is "Obligations of distributors" (real Article 24's distributor content appears, in this DB, under a different article number not directly checked) | Whether company is a product manufacturer integrating high-risk AI | PARTIAL |
| Article 25 — Responsibilities along the AI value chain | Whether company substantially modifies/rebrands a third-party AI system (which converts it into a "provider") | PARTIAL |
| Article 26 — Obligations of deployers of high-risk AI systems | Whether company deploys (uses) high-risk AI under its own authority, with oversight/logging/monitoring in place | PARTIAL (`role` concept exists, no oversight/logging-policy field) |
| Article 27 — Fundamental rights impact assessment for high-risk AI systems | Whether deployer is a public body or private entity providing public services (education, banking, insurance, healthcare, social services) using Annex III high-risk AI | NO — `is_public_body`/`provides_public_service` don't exist; `b2b_or_b2c` and `industry` are not sufficient substitutes |
| Article 40 — Harmonised standards and standardisation deliverables | None actionable (presumption-of-conformity mechanism) | N/A |
| Article 41 — Common specifications | None actionable | N/A |
| Article 42 — Presumption of conformity with certain requirements | None actionable | N/A |
| Article 43 — Conformity assessment | Whether the high-risk system has undergone the required conformity-assessment procedure (self-assessment vs third-party, depending on Annex III category) | NO — no `conformity_assessment_status` field |
| Article 44 — Certificates | Whether a notified-body certificate exists and its expiry (max 5 years) | NO |
| Article 45 — Extraordinary functioning of notified bodies (DB title: "Extraordinary functioning of notified bodies" — matches real Article 45 by title; content checked is informational) | None actionable | N/A |
| Article 46 — Appeal against decisions of notified bodies — **title drift**: DB content is "Derogation from conformity assessment procedure" (real Article 46), but DB's title field says "Appeal against decisions of notified bodies" (real Article 46's actual title is "Derogation from conformity assessment procedure"; "Appeal" is real Article 46... wait — checked: real Article 46 title IS "Derogation from conformity assessment procedure", confirmed) | Whether an emergency derogation from conformity assessment was used | NO |
| Article 47 — EU declaration of conformity | Whether an EU declaration of conformity has been drawn up | NO |
| Article 48 — CE marking of conformity | Whether CE marking has been affixed | NO |
| Article 49 — Registration | Whether the system is registered in the EU database (Article 71) | NO |
| Article 50 — Transparency obligations for certain AI systems | Whether the company uses chatbots, generates synthetic media, or uses emotion-recognition/biometric-categorisation systems that interact with natural persons | NO — `uses_chatbot`, `generates_synthetic_content`, `uses_emotion_recognition` referenced in `evaluation_logic` don't exist anywhere; only the generic `uses_ai` boolean exists |
| Article 51 — Classification of general-purpose AI models as models with systemic risk | MATCH | Whether the company's GPAI model exceeds the 10^25 FLOPs systemic-risk threshold |
| Article 52 — Obligations for providers of general-purpose AI models | **MISMATCH** | Whether company is a GPAI model provider with technical documentation, downstream-provider info, copyright policy, training-data summary in place |
| Article 53 — Obligations for providers of general-purpose AI models with systemic risk | **MISMATCH** | Whether GPAI model has model evaluation/adversarial testing, systemic risk mitigation, incident reporting, cybersecurity measures |
| Article 54 — Codes of practice | **MISMATCH** | None actionable (voluntary compliance mechanism) |
| Article 55 — Other measures in support of innovation for providers of GPAI models | **MISMATCH** | None actionable |
| Article 56 — Qualitative description of parameters relevant for classification | **MISMATCH** | None actionable directly (informational criteria list) |
| Article 57 — AI regulatory sandboxes | None actionable (Member State infrastructure obligation) | N/A |
| Article 58 — Detailed arrangements for AI regulatory sandboxes | None actionable | N/A |
| Article 59 — Further processing of personal data for developing certain AI systems in the public interest in the AI regulatory sandbox | None actionable | N/A |
| Article 60 — Testing of high-risk AI systems in real world conditions outside AI regulatory sandboxes | Whether company conducts real-world testing of high-risk AI outside a sandbox | NO |
| Article 61 — Measures for providers and deployers, in particular SMEs including start-ups | None actionable for the DB's stated content (Member State SME support duty); the missing real-61 topic would need consent-documentation tracking for real-world AI testing | NO (for missing real Art. 61) |
| Article 62 — Mechanism to report concerns about AI systems | Whether company is a microenterprise eligible for simplified QMS compliance under Article 63 | YES — `company_size` (loosely) |
| Article 63 — Derogations for specific operators | Whether company qualifies as a microenterprise | YES — `company_size` |
| Article 71 — EU database for high-risk AI systems | Whether the high-risk AI system is registered in the EU database | NO |
| Article 72 — Post-market monitoring by providers and post-market monitoring plan for high-risk AI systems | MATCH | Whether a post-market monitoring plan exists |
| Article 73 — Reporting of serious incidents by providers of high-risk AI systems | MATCH | Whether a serious-incident reporting process exists |
| Article 74 — Market surveillance activities | PARTIAL | None directly actionable |
| Article 75 — Mutual assistance, market surveillance activities and investigations of AI systems involving authorities from multiple Member States | MATCH | None actionable |
| Article 76 — Oversight of testing in real world conditions | MATCH | None actionable |
| Article 77 — Obligations of deployers | **MISMATCH** | (duplicate of Article 26's data needs) |
| Article 78 — Confidentiality | MATCH | None actionable |
| Article 79 — Penalties | **MISMATCH** | None actionable for DB's stated content |
| Article 80 — Penalties for providers of general-purpose AI models | **MISMATCH** | Whether GPAI model presents systemic risk (DB's stated topic) |
| Article 81 — Procedural rules for the adoption of supervisory measures by the AI Office | **MISMATCH** | None actionable |
| Article 82 — Right to be heard and access to the file | **MISMATCH** | None actionable |
| Article 83 — Limitation periods for the imposition of penalties | **MISMATCH** | None actionable |
| Article 84 — Publication of decisions | **MISMATCH** | None actionable |
| Article 85 — European AI Office | **MISMATCH** | Whether company has a process for handling AI-related complaints from affected persons |
| Article 86 — Right to explanation | MATCH | Whether the company has a process to provide affected persons with explanations of high-risk AI decisions |
| Article 87 — Reporting of breaches and protection of reporting persons | MATCH | None actionable (whistleblower-protection duty) |
| Article 88 — AI systems and GPAI models for general security purposes | **MISMATCH** | None actionable for DB's stated topic (military/security AI exemption is actually covered under Article 2(3), not 88) |
| Article 89 — AI systems with specific transparency obligations | **MISMATCH** | (duplicate of Article 50 topic) |
| Article 90 — European Artificial Intelligence Board | **MISMATCH** | None actionable |
| Article 91 — Tasks of the AI Board | **MISMATCH** | Whether company can respond to AI Office documentation requests for its GPAI model |
| Article 92 — Scientific panel of independent experts | **MISMATCH** | None actionable |
| Article 93 — Advisory forum | **MISMATCH** | None actionable |
| Article 94 — Involvement of the Advisory Forum in the functioning of the Board | **MISMATCH** | Whether company (as a GPAI provider) has been given due-process rights before AI Office sanctions |
| Article 95 — Codes of conduct for voluntary application of specific requirements | MATCH | None actionable (voluntary scheme) |
| Article 96 — Guidelines from the Commission on the implementation of this Regulation | MATCH | None actionable |
| Article 97 — Exercise of the delegation | MATCH | None actionable |
| Article 98 — Committee procedure | MATCH | None actionable |
| Article 99 — Amendments to Regulation (EU) No 300/2008 | **MISMATCH** — real Article 99 is "Penalties" (the core fines article: EUR 35M/7% for Art. 5 violations, EUR 15M/3% for most other operator violations, EUR 7.5M/1% for misleading information to authorities) | None actionable directly, but this is the article that determines fine exposure for every other gap found elsewhere in this audit — its complete absence under the correct number is a significant content gap |
| Article 100 — Amendments to Regulation (EU) No 167/2013 | **MISMATCH** — real Article 100 is "Administrative fines on Union institutions, bodies, offices and agencies" | N/A |
| Article 101 — Amendments to Regulation (EU) No 168/2013 | **MISMATCH** — real Article 101 is "Fines for providers of general-purpose AI models" (up to EUR 15M/3% turnover) | None actionable directly, but this is the GPAI-specific fines article missing from the DB under its correct number |
| Article 102 — Amendments to Directive 2014/90/EU | **MISMATCH** — real Article 102 is "Amendment to Regulation (EC) No 300/2008" | N/A |
| Article 103 — Amendments to Directive (EU) 2016/797 | **MISMATCH** — real Article 103 is "Amendment to Regulation (EU) No 167/2013" | N/A |
| Article 104 — Amendments to Regulation (EU) 2018/858 | **MISMATCH** | N/A |
| Article 105 — Amendments to Regulation (EU) 2019/2144 | **MISMATCH** — real Article 105 is "Amendment to Directive 2014/90/EU" | N/A |
| Article 106 — Amendments to Regulation (EU) 2020/1056 | **MISMATCH** — likely a fabricated/incorrect amended-instrument reference | N/A |
| Article 107 — Amendments to Regulation (EU) No 575/2013 | **MISMATCH** — likely fabricated | N/A |
| Article 108 — Amendments to Directive 2013/36/EU | **MISMATCH** — likely fabricated | N/A |
| Article 109 — AI systems already placed on the market or put into service | **MISMATCH** — DB title for 109 actually correctly describes the *topic* of real Article 111, just three articles early | N/A |
| Article 110 — Evaluation and review | **MISMATCH** — DB title actually correctly describes real Article 112's topic | N/A |
| Article 111 — Repeal | **MISMATCH** — fabricated article topic | N/A |
| Article 112 — Transitional provisions | **MISMATCH** | N/A |
| Article 113 — Entry into force and application | MATCH | None actionable |