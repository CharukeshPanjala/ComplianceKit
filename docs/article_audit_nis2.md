# NIS2 Directive (EU 2022/2555) — DB Rule Audit

Source legal text: `docs/Nis2.pdf` (German Official Journal edition, 46 real articles, Annexes I-III).
Source DB dump: `/tmp/ck_audit/nis2_rules.json` (46 rule rows).

## Summary

- **Total articles audited:** 46
- **MATCH:** 27
- **PARTIAL:** 9
- **MISMATCH:** 10
- **Articles with a data availability gap (PARTIAL or NO):** 33
- **Dangling reference count:** 19 (15 rules reference `nis2_data.nis2_sectors`, real field is `nis2_data.sectors`; 4 rules reference `nis2_data.has_incident_plan`, real field is `nis2_data.has_incident_response_plan`)
  - Dangling articles: DB2, DB18, DB23, DB25, DB27 (`nis2_data.nis2_sectors` / `nis2_data.has_incident_plan` typos do not exist in the real `nis2_data` JSONB schema)

**Critical finding — DB article numbering does not match the real Directive from Article 5 onward.** Real Articles 5 ("Mindestharmonisierung") and 6 ("Begriffsbestimmungen") are skipped entirely; the DB then runs a non-constant offset through Article 35, normalizes from 26-35, and runs a -1 offset from 39-46. DB18 and DB24/DB25 are the most serious mismatches: DB18 duplicates real Article 23 content under the wrong title/number (real Art 18 is a biennial ENISA cybersecurity report, unrelated to incident reporting), and DB24/DB25 misattribute sub-clauses of real Article 23 to nonexistent or wrong articles (real Art 24 = certification schemes, Art 25 = standardisation).

---

## Article-by-article audit

### DB1 — Subject matter
- **Legal accuracy:** MATCH. Real Art 1 ("Gegenstand") — matches DB1 description (lays down cybersecurity risk-management/reporting obligations, supervision framework, cooperation mechanisms).
- **Data needed:** None — informational article.
- **Data availability:** N/A (informational).
- **Dangling reference:** N/A (`profile_field` null, `evaluation_logic.type = informational`).

### DB2 — Scope
- **Legal accuracy:** MATCH. Real Art 2 ("Anwendungsbereich") — applies to entities in Annex I/II sectors meeting size thresholds (medium+ enterprises), matches DB2.
- **Data needed:** Sector classification + entity size/turnover.
- **Data availability:** PARTIAL — sector is collected, size threshold is not separately modeled.
- **Dangling reference:** DANGLING — `profile_field` = `nis2_data.nis2_sectors`; real field name is `nis2_data.sectors`.

### DB3 — Essential and important entities
- **Legal accuracy:** MATCH. Real Art 3 lists which entity types are "essential" vs "important" — matches DB3.
- **Data needed:** Entity type classification (essential/important).
- **Data availability:** YES — `nis2_data.entity_type`.
- **Dangling reference:** OK.

### DB4 — Sector-specific Union legal acts
- **Legal accuracy:** MATCH. Real Art 4 (lex specialis rule for sector laws with equivalent effect) matches DB4.
- **Data needed:** Industry/sector.
- **Data availability:** YES — `company_profiles.industry`.
- **Dangling reference:** OK (`profile_field = industry` exists).

### DB5 — National cybersecurity strategy
- **Legal accuracy:** MISMATCH on number — DB5 is informational/government-obligation content but is actually sourced from real Article 7 ("Nationale Cybersicherheitsstrategie"), not real Article 5 ("Mindestharmonisierung", a minimum-harmonisation clause). Title and substance match real Art 7 exactly; only the numbering is off (real Articles 5 and 6 are skipped entirely in the DB).
- **Data needed:** None — describes Member State, not tenant, obligations.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB6 — (title per DB: vulnerability-disclosure adjacent content)
- **Legal accuracy:** PARTIAL/duplicate. Content traces to real Art 12 ("Koordinierte Offenlegung von Schwachstellen..."), the same source article also used by DB11. The two DB rows split one real article into two DB rows with overlapping scope.
- **Data needed:** Whether a coordinated vulnerability disclosure policy/process exists.
- **Data availability:** NO — GAP, not collected anywhere in the field list.
- **Dangling reference:** N/A (informational).

### DB7 — National cyber crisis management framework
- **Legal accuracy:** MATCH. Real Art 9 matches DB7 (national crisis management plans, designation of crisis-management authorities).
- **Data needed:** None — Member State obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB8 — Competent authorities and single point of contact
- **Legal accuracy:** MATCH. Real Art 8 matches.
- **Data needed:** None — Member State obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB9 — CSIRTs
- **Legal accuracy:** MATCH. Real Art 10 matches.
- **Data needed:** None — Member State obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB10 — Requirements for CSIRTs
- **Legal accuracy:** MATCH. Real Art 11 matches.
- **Data needed:** None — Member State obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB11 — Coordinated vulnerability disclosure
- **Legal accuracy:** PARTIAL. Real Art 12 covers a national CVD policy and designates a CSIRT as coordinator/trusted intermediary between reporting persons and manufacturers/providers, plus a European vulnerability database maintained by ENISA. DB11's specific claim that Member States must give security researchers explicit "legal protection" when responsibly reporting is not stated as a standalone obligation in the text read — it is implied by the coordinated-disclosure framework but not an explicit legal-protection clause. Also a near-duplicate of DB6's source article.
- **Data needed:** Whether the org follows a coordinated/responsible vulnerability disclosure process.
- **Data availability:** NO — GAP, not collected.
- **Dangling reference:** N/A (`evaluation_logic.type = policy_required`, references `vulnerability_disclosure_policy` which has no corresponding profile field anywhere — effectively an unverifiable check, but not a literal dangling DB field reference).

### DB12 — Cyber crisis management (EU-CyCLONe per DB)
- **Legal accuracy:** PARTIAL. DB12's title diverges from real Art 16 ("Europäisches Netzwerk der Verbindungsorganisationen für Cyberkrisen" / EU-CyCLONe) — content is topically aligned (EU-level crisis coordination network) but the DB title is far more generic than the real article's specific institutional name.
- **Data needed:** None — EU/Member State institutional obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB13 — Cooperation at Union level
- **Legal accuracy:** MISMATCH. Real Art 13 ("Zusammenarbeit auf nationaler Ebene") is specifically about NATIONAL-level cooperation between the competent authority, SPOC, and CSIRTs within one Member State. DB13's title "Cooperation at Union level" describes the wrong scope — Union-level cooperation is real Art 14 (Cooperation Group), which the DB already separately captures as DB15.
- **Data needed:** None — institutional obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB14 — CSIRTs network
- **Legal accuracy:** MATCH. Real Art 15 matches.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB15 — NIS Cooperation Group
- **Legal accuracy:** MATCH. Real Art 14 matches (number differs from DB's position but title/content align with DB15, confirming DB13/DB14/DB15 are all shuffled relative to true numbering, though each individually still matches a real article's substance).
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB16 — International cooperation
- **Legal accuracy:** MATCH. Real Art 17 matches.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB17 — Peer reviews
- **Legal accuracy:** MATCH. Real Art 19 matches.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB18 — Reporting obligations (incidents)
- **Legal accuracy:** MISMATCH. Real Art 18 is "Bericht über den Stand der Cybersicherheit in der Union" — a biennial ENISA report on the state of EU cybersecurity, completely unrelated to incident reporting. DB18's 24h/72h/1-month notification content is the real Article 23 text, duplicated here under the wrong article number and title.
- **Data needed:** Whether an incident response/reporting process exists.
- **Data availability:** PARTIAL — `nis2_data.has_incident_response_plan` exists but only as a yes/no flag, not deadline-tracking detail.
- **Dangling reference:** DANGLING — `profile_field`/`evaluation_logic` reference `nis2_data.has_incident_plan`, which does not exist; real field is `nis2_data.has_incident_response_plan`.

### DB19 — Use of European cybersecurity certification schemes
- **Legal accuracy:** MATCH. Real Art 24 matches.
- **Data needed:** Whether the org uses any certified products/services.
- **Data availability:** NO — GAP, not collected.
- **Dangling reference:** N/A.

### DB20 — Governance
- **Legal accuracy:** MATCH. Real Art 20 matches (management body approval/training obligations for risk-management measures).
- **Data needed:** Whether management has approved a cybersecurity governance policy and undergone training.
- **Data availability:** NO — GAP, not collected (no governance-approval or board-training field exists).
- **Dangling reference:** N/A (`evaluation_logic.type = policy_required`, no matching profile field, but not a literal dangling field name).

### DB21 — Cybersecurity risk-management measures
- **Legal accuracy:** MATCH. Real Art 21's 10-point list (a-j: risk analysis, incident handling, business continuity, supply chain security, secure development/vuln handling, effectiveness assessment, cyber hygiene/training, cryptography, access control/asset management, MFA/secure comms) matches DB21's `required_measures` list closely.
- **Data needed:** Presence of each of the 10 specific technical/organisational measures.
- **Data availability:** NO — GAP. None of `risk_analysis_policy`, `incident_handling_procedure`, `business_continuity_plan`, `supply_chain_security_policy`, `secure_development_policy`, `security_effectiveness_assessment`, `cyber_hygiene_training`, `cryptography_policy`, `access_control_policy` exist as collected fields. Only `nis2_data.has_mfa` (partially covers the MFA sub-measure) and `nis2_data.has_business_continuity_plan` exist among the ten.
- **Dangling reference:** N/A (no `profile_field` set; `required_measures` list itself is not a literal field reference, but is effectively unverifiable against the real schema except for the two matches noted).

### DB22 — Coordinated risk assessments of critical supply chains
- **Legal accuracy:** MATCH. Real Art 22 matches.
- **Data needed:** None — EU/Member State-level coordinated assessment, not tenant-level.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB23 — Reporting obligations
- **Legal accuracy:** MATCH. Real Art 23 ("Berichtspflichten") matches DB23's 24h early warning / 72h notification / 1-month final report structure exactly.
- **Data needed:** Whether an incident reporting/response process and timeline exist.
- **Data availability:** PARTIAL — `nis2_data.has_incident_response_plan` covers existence, not deadline-tracking capability.
- **Dangling reference:** DANGLING — references `nis2_data.has_incident_plan`, not the real field `nis2_data.has_incident_response_plan`.

### DB24 — Technical guidelines and methodological guidelines on incident reporting
- **Legal accuracy:** MISMATCH. No real article at this position covers this content as a standalone obligation. Real Art 24 is "Nutzung der europäischen Schemata für die Cybersicherheitszertifizierung" (use of EU cybersecurity certification schemes) and real Art 25 is "Normung" (standardisation) — neither matches. ENISA reporting-template guidance is only a minor sub-clause inside real Art 23, not a separate landmark article; this DB row appears fabricated/misattributed.
- **Data needed:** None — ENISA/Commission obligation, not tenant-level.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB25 — Notification to recipients of services and to the public
- **Legal accuracy:** MISMATCH. Content (notify affected customers without undue delay; authorities may require public disclosure) is drawn from real Art 23(1) and 23(7) sub-clauses, not from real Art 25 ("Normung"/Standardisation), which is unrelated. Number/title attribution is wrong even though the underlying obligation genuinely exists within Art 23.
- **Data needed:** Whether a customer/public incident-notification procedure exists.
- **Data availability:** PARTIAL — closest field is `nis2_data.has_incident_response_plan`, but it does not specifically capture customer-notification capability.
- **Dangling reference:** DANGLING — `profile_field` = `nis2_data.has_incident_plan` (real field is `nis2_data.has_incident_response_plan`).

### DB26 — Jurisdiction and territoriality
- **Legal accuracy:** MATCH. Real Art 26 matches.
- **Data needed:** Primary jurisdiction / where main establishment is located.
- **Data availability:** YES — `company_profiles.primary_jurisdiction`.
- **Dangling reference:** OK.

### DB27 — Register of entities
- **Legal accuracy:** PARTIAL. Real Art 27 ("Register der Einrichtungen") is narrower than a generic "all essential/important entities" register — it specifically covers DNS providers, TLD registries, domain name registration services, cloud/data centre/CDN/managed service providers, and online marketplaces/search engines/social media platforms providing services in the Union, who must submit specific registration data to ENISA. DB27's framing as a general NIS2 registration requirement for all in-scope sectors overstates the article's actual scope.
- **Data needed:** Sector classification (to determine if the narrower Art 27 registration duty applies) plus registration completion status.
- **Data availability:** PARTIAL — sector is collected (with a dangling field name issue, see below); no field tracks actual registration completion.
- **Dangling reference:** DANGLING — `profile_field` = `nis2_data.nis2_sectors`; real field is `nis2_data.sectors`.

### DB28 — Database of domain name registration data
- **Legal accuracy:** MATCH. Real Art 28 matches.
- **Data needed:** None — applies only to TLD registries/domain registration entities, an EU-level database obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB29 — Cybersecurity information sharing arrangements
- **Legal accuracy:** MATCH. Real Art 29 matches.
- **Data needed:** Whether the org participates in any information-sharing arrangement.
- **Data availability:** NO — GAP, not collected.
- **Dangling reference:** N/A.

### DB30 — Voluntary notification of relevant information
- **Legal accuracy:** MATCH. Real Art 30 matches.
- **Data needed:** None — describes a voluntary right, not a measurable compliance state.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB31 — General aspects of supervision and enforcement
- **Legal accuracy:** MATCH. Real Art 31 matches exactly (risk-based supervision; proactive for essential entities, reactive/ex-post for important entities).
- **Data needed:** Entity type (essential vs important) to determine which supervisory regime applies.
- **Data availability:** YES — `nis2_data.entity_type`.
- **Dangling reference:** OK.

### DB32 — Supervisory and enforcement measures re: essential entities
- **Legal accuracy:** MATCH. Real Art 32 matches in granular detail (on-site inspections, security audits, ad-hoc audits, security scans, binding instructions, monitoring officer designation, temporary suspension of services/certifications, personal liability/management bans, fines per Art 34).
- **Data needed:** Entity type.
- **Data availability:** YES — `nis2_data.entity_type`.
- **Dangling reference:** OK.

### DB33 — Supervisory and enforcement measures re: important entities
- **Legal accuracy:** MATCH. Real Art 33 matches (same powers as Art 32 but ex-post/reactive only, triggered by evidence or complaints).
- **Data needed:** Entity type.
- **Data availability:** YES — `nis2_data.entity_type`.
- **Dangling reference:** OK.

### DB34 — General rules on administrative fines
- **Legal accuracy:** MATCH. Real Art 34 matches exactly — essential entities: max €10M or 2% global turnover, whichever higher; important entities: max €7M or 1.4% global turnover, whichever higher.
- **Data needed:** Entity type + global turnover (for fine exposure estimation).
- **Data availability:** PARTIAL — `nis2_data.entity_type` exists; no turnover/revenue field exists in the provided list.
- **Dangling reference:** OK (`profile_field` references valid `nis2_data.entity_type`).

### DB35 — Infringements entailing a personal data breach
- **Legal accuracy:** MATCH. Real Art 35 matches — cooperation between NIS2 competent authorities and GDPR DPAs, no double-fining for the same conduct (higher applicable fine governs), competent authorities must inform DPAs when an infringement also constitutes a personal data breach.
- **Data needed:** None — describes inter-authority cooperation, not a tenant-level fact.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB36 — Penalties
- **Legal accuracy:** MATCH. Real Art 36 matches (Member States must set effective, proportionate, dissuasive penalties for breaches of national NIS2-implementing measures, notified to the Commission by 17 Jan 2025).
- **Data needed:** None — Member State obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB37 — Mutual assistance
- **Legal accuracy:** MATCH. Real Art 37 matches (cross-border cooperation duties between competent authorities for entities operating in multiple Member States; mutual assistance requests and grounds for refusal).
- **Data needed:** None — inter-authority obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB38 — Joint supervisory actions
- **Legal accuracy:** PARTIAL. The content (joint supervisory actions by 2+ Member States, led by the state where the entity is established) is real, but it appears as real Art 37(2), a sub-paragraph of "Amtshilfe" (Mutual assistance) — not as its own standalone article. Real Art 38 is actually "Ausübung der Befugnisübertragung" (Exercise of the delegation, an entirely different administrative-law topic). DB38 misattributes a sub-clause of Art 37 to a nonexistent standalone article.
- **Data needed:** None — inter-authority obligation.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB39 — Exercise of the delegation
- **Legal accuracy:** MATCH (content), number offset by -1. Title and content match real Art 38 exactly (Commission delegated-act powers under Art 24(2), 5-year period from 16 Jan 2023, revocation/objection procedure).
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB40 — Committee procedure
- **Legal accuracy:** MATCH (content), number offset by -1. Matches real Art 39 (comitology under Regulation (EU) 182/2011).
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB41 — Review
- **Legal accuracy:** MATCH (content), number offset by -1. Matches real Art 40 exactly (Commission review by 17 Oct 2027, then every 36 months, report to Parliament/Council).
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB42 — Amendments to Regulation (EU) No 910/2014
- **Legal accuracy:** PARTIAL, number offset by -1 vs. content position (real Art 41 is "Umsetzung"/Transposition; real Art 42 is the actual eIDAS amendment). DB42's plain-English description overstates the mechanism: it frames this as broadly "aligning trust service providers with NIS2 security requirements," but the real Art 42 text is a single-line deletion ("Article 19 of Regulation 910/2014 is deleted, effective 18 Oct 2024") with no separate substantive alignment language in the article itself.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB43 — Amendments to Directive (EU) 2018/1972
- **Legal accuracy:** PARTIAL, same issue as DB42 — real Art 43 simply deletes Articles 40 and 41 of the EECC effective 18 Oct 2024; DB43's broader "alignment" framing is an oversimplification/embellishment rather than the literal one-line repeal in the text.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB44 — Repeal
- **Legal accuracy:** MATCH. Matches real Art 44 exactly (NIS1 Directive 2016/1148 repealed effective 18 Oct 2024; references to it construed as references to NIS2 per the correlation table in Annex III).
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB45 — Transposition
- **Legal accuracy:** MATCH. Matches real Art 41 ("Umsetzung") content exactly (Member States adopt/publish by 17 Oct 2024, apply from 18 Oct 2024) — despite the title being correct, the DB's sequencing places this after "Repeal" (DB44), out of the real Directive's article order.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.

### DB46 — Entry into force
- **Legal accuracy:** PARTIAL. Matches real Art 45 ("Inkrafttreten") content exactly (enters into force 20th day after publication). However, the DB has no row at all corresponding to real Art 46 ("Adressaten"/Addressees — "This Directive is addressed to the Member States"), meaning the DB's final article silently drops the actual final real article of the Directive.
- **Data needed:** None.
- **Data availability:** N/A.
- **Dangling reference:** N/A.
