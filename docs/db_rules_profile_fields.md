# DB Rules — Profile Field Reference

Live snapshot of all rules in the DB with their `profile_field` (pf) column.
Used to cross-check scorer/applicability field references against real DB state.

---

## GDPR RULES (in DB)

| Article | Title | profile_field |
|---------|-------|---------------|
| Art.1 | Subject-matter and objectives | (none) |
| Art.2 | Material scope | (none) |
| Art.3 | Territorial scope | `primary_jurisdiction` |
| Art.4 | Definitions | (none) |
| Art.5 | Principles relating to processing of personal data | (none) |
| Art.6 | Lawfulness of processing | `gdpr_data.lawful_bases` |
| Art.7 | Conditions for consent | `gdpr_data.lawful_bases` |
| Art.8 | Conditions applicable to child's consent | `gdpr_data.processes_children_data` |
| Art.9 | Processing of special categories of personal data | `data_categories_processed` |
| Art.10 | Processing of personal data relating to criminal convictions | `data_categories_processed` |
| Art.11 | Processing which does not require identification | (none) |
| Art.12 | Transparent information, communication | (none) |
| Art.13 | Information to be provided where personal data are collected from the data subject | (none) |
| Art.14 | Information to be provided where personal data have not been obtained | (none) |
| Art.15 | Right of access by the data subject | (none) |
| Art.16 | Right to rectification | (none) |
| Art.17 | Right to erasure ('right to be forgotten') | (none) |
| Art.18 | Right to restriction of processing | (none) |
| Art.19 | Notification obligation regarding rectification or erasure | `gdpr_data.uses_data_processors` |
| Art.20 | Right to data portability | `gdpr_data.lawful_bases` |
| Art.21 | Right to object | (none) |
| Art.22 | Automated individual decision-making, including profiling | `ai_act_data.uses_ai` |
| Art.23 | Restrictions | (none) |
| Art.24 | Responsibility of the controller | (none) |
| Art.25 | Data protection by design and by default | (none) |
| Art.26 | Joint controllers | (none) |
| Art.27 | Representatives of controllers not established in the Union | `primary_jurisdiction` |
| Art.28 | Processor | `gdpr_data.uses_data_processors` |
| Art.29 | Processing under the authority of controller or processor | `gdpr_data.uses_data_processors` |
| Art.30 | Records of processing activities | (none) |
| Art.31 | Cooperation with the supervisory authority | (none) |
| Art.32 | Security of processing | `uses_cloud_services` |
| Art.33 | Notification of a personal data breach | `gdpr_data.has_breach_procedure` |
| Art.34 | Communication of a personal data breach to the data subject | `gdpr_data.has_breach_procedure` |
| Art.35 | Data protection impact assessment | `gdpr_data.has_dpia` |
| Art.36 | Prior consultation | `gdpr_data.has_dpia` |
| Art.37 | Designation of the data protection officer | `has_compliance_officer` |
| Art.38 | Position of the data protection officer | `has_compliance_officer` |
| Art.39 | Tasks of the data protection officer | `has_compliance_officer` |
| Art.40 | Codes of conduct | (none) |
| Art.41 | Monitoring of approved codes of conduct | (none) |
| Art.42 | Certification | `certifications` |
| Art.43 | Certification bodies | (none) |
| Art.44 | General principle for transfers | `gdpr_data.transfers_outside_eea` |
| Art.45 | Transfers on the basis of an adequacy decision | `gdpr_data.transfers_outside_eea` |
| Art.46 | Transfers subject to appropriate safeguards | `gdpr_data.transfers_outside_eea` |
| Art.47 | Binding corporate rules | (none) |
| Art.48 | Transfers or disclosures not authorised by Union law | `gdpr_data.transfers_outside_eea` |
| Art.49 | Derogations for specific situations | `gdpr_data.transfers_outside_eea` |
| Art.50 | International cooperation | (none) |
| Art.51 | Supervisory authority | (none) |
| Art.52 | Independence | (none) |
| Art.53 | General conditions for members | (none) |
| Art.54 | Rules on establishment | (none) |
| Art.55 | Competence | (none) |
| Art.56 | Competence of lead supervisory authority | (none) |
| Art.57 | Tasks | (none) |
| Art.58 | Powers | (none) |
| Art.59 | Activity reports | (none) |
| Art.60 | Cooperation between lead and concerned authorities | (none) |
| Art.61 | Mutual assistance | (none) |
| Art.62 | Joint operations | (none) |
| Art.63 | Consistency mechanism | (none) |
| Art.64 | Opinion of the Board | (none) |
| Art.65 | Dispute resolution by the Board | (none) |
| Art.66 | Urgency procedure | (none) |
| Art.67 | Exchange of information | (none) |
| Art.68 | European Data Protection Board | (none) |
| Art.69 | Independence (EDPB) | (none) |
| Art.70 | Tasks of the Board | (none) |
| Art.71 | Reports | (none) |
| Art.72 | Procedure | (none) |
| Art.73 | Chair | (none) |
| Art.74 | Tasks of the Chair | (none) |
| Art.75 | Secretariat | (none) |
| Art.76 | Confidentiality | (none) |
| Art.77 | Right to lodge a complaint | (none) |
| Art.78 | Judicial remedy against supervisory authority | (none) |
| Art.79 | Judicial remedy against controller/processor | (none) |
| Art.80 | Representation of data subjects | (none) |
| Art.81 | Suspension of proceedings | (none) |
| Art.82 | Right to compensation and liability | (none) |
| Art.83 | Administrative fines | (none) |
| Art.84 | Penalties | (none) |
| Art.85 | Freedom of expression and information | (none) |
| Art.86 | Public access to official documents | (none) |
| Art.87 | National identification number | (none) |
| Art.88 | Processing in employment context | (none) |
| Art.89 | Safeguards for archiving/research/statistics | (none) |
| Art.90 | Obligations of secrecy | (none) |
| Art.91 | Churches and religious associations | (none) |
| Art.92 | Exercise of the delegation | (none) |
| Art.93 | Committee procedure | (none) |
| Art.94 | Repeal of Directive 95/46/EC | (none) |
| Art.95 | Relationship with ePrivacy Directive | (none) |
| Art.96 | Relationship with prior agreements | (none) |
| Art.97 | Commission reports | (none) |
| Art.98 | Review of other Union legal acts | (none) |
| Art.99 | Entry into force and application | (none) |

---

## NIS2 RULES (in DB)

| Article | Title | profile_field |
|---------|-------|---------------|
| Art.1 | Subject matter | (none) |
| Art.2 | Scope | `nis2_data.sectors` |
| Art.3 | Essential and important entities | `nis2_data.entity_type` |
| Art.4 | Sector-specific Union legal acts | `industry` |
| Art.5 | Minimum harmonisation | (none) |
| Art.6 | Definitions | (none) |
| Art.7 | National cybersecurity strategy | (none) |
| Art.8 | Competent authorities and single point of contact | (none) |
| Art.9 | National cyber crisis management framework | (none) |
| Art.10 | CSIRTs | (none) |
| Art.11 | Requirements for CSIRTs | (none) |
| Art.12 | Coordinated vulnerability disclosure | (none) |
| Art.13 | Cooperation at national level | (none) |
| Art.14 | NIS Cooperation Group | (none) |
| Art.15 | CSIRTs network | (none) |
| Art.16 | Cyber crisis management | (none) |
| Art.17 | International cooperation | (none) |
| Art.18 | Report on the state of cybersecurity in the Union | (none) |
| Art.19 | Peer reviews | (none) |
| Art.20 | Governance | (none) |
| Art.21 | Cybersecurity risk-management measures | (none) |
| Art.22 | Union level coordinated security risk assessments | (none) |
| Art.23 | Reporting obligations | `nis2_data.has_incident_response_plan` |
| Art.24 | Use of European cybersecurity certification schemes | (none) |
| Art.25 | Standardisation | (none) |
| Art.26 | Jurisdiction and territoriality | `primary_jurisdiction` |
| Art.27 | Register of essential and important entities | `nis2_data.sectors` |
| Art.28 | Database of domain name registration data | (none) |
| Art.29 | Cybersecurity information sharing arrangements | (none) |
| Art.30 | Voluntary notification of relevant information | (none) |
| Art.31 | General aspects of supervision and enforcement | `nis2_data.entity_type` |
| Art.32 | Supervisory and enforcement measures in relation to essential entities | `nis2_data.entity_type` |
| Art.33 | Supervisory and enforcement measures in relation to important entities | `nis2_data.entity_type` |
| Art.34 | General rules on administrative fines | `nis2_data.entity_type` |
| Art.35 | Infringements entailing a personal data breach | (none) |
| Art.36 | Penalties | (none) |
| Art.37 | Mutual assistance | (none) |
| Art.38 | Exercise of the delegation | (none) |
| Art.39 | Committee procedure | (none) |
| Art.40 | Review | (none) |
| Art.41 | Transposition | (none) |
| Art.42 | Amendments to Regulation (EU) No 910/2014 | (none) |
| Art.43 | Amendments to Directive (EU) 2018/1972 | (none) |
| Art.44 | Repeal | (none) |
| Art.45 | Entry into force | (none) |
| Art.46 | Addressees | (none) |

---

## EU AI ACT RULES (in DB)

| Article | Title | profile_field |
|---------|-------|---------------|
| Art.1 | Subject matter | (none) |
| Art.2 | Scope | `ai_act_data.uses_ai` |
| Art.3 | Definitions | (none) |
| Art.4 | AI literacy | (none) |
| Art.5 | Prohibited AI practices | `ai_act_data.uses_ai` |
| Art.6 | Classification rules for high-risk AI systems | `ai_act_data.high_risk_ai_categories` |
| Art.7 | Amendments to Annex III | (none) |
| Art.8 | Compliance with the requirements | `ai_act_data.high_risk_ai_categories` |
| Art.9 | Risk management system | `ai_act_data.high_risk_ai_categories` |
| Art.10 | Data and data governance | `ai_act_data.high_risk_ai_categories` |
| Art.11 | Technical documentation | `ai_act_data.high_risk_ai_categories` |
| Art.12 | Record-keeping | `ai_act_data.high_risk_ai_categories` |
| Art.13 | Transparency and provision of information to deployers | `ai_act_data.high_risk_ai_categories` |
| Art.14 | Human oversight | `ai_act_data.high_risk_ai_categories` |
| Art.15 | Accuracy, robustness and cybersecurity | `ai_act_data.high_risk_ai_categories` |
| Art.16 | Obligations of providers of high-risk AI systems | `ai_act_data.ai_role` |
| Art.17 | Quality management system | `ai_act_data.ai_role` |
| Art.18 | Documentation keeping | `ai_act_data.ai_role` |
| Art.19 | Automatically generated logs | `ai_act_data.high_risk_ai_categories` |
| Art.20 | Corrective actions and duty of information | `ai_act_data.ai_role` |
| Art.21 | Cooperation with competent authorities | `ai_act_data.ai_role` |
| Art.22 | Authorised representatives of providers not established in the Union | `primary_jurisdiction` |
| Art.23 | Obligations of importers | `ai_act_data.ai_role` |
| Art.24 | Obligations of product manufacturers | `ai_act_data.ai_role` |
| Art.25 | Responsibilities along the AI value chain | `ai_act_data.ai_role` |
| Art.26 | Obligations of deployers of high-risk AI systems | `ai_act_data.ai_role` |
| Art.27 | Fundamental rights impact assessment for high-risk AI systems | `ai_act_data.high_risk_ai_categories` |
| Art.28 | Notifying authorities | (none) |
| Art.29 | Application of a conformity assessment body for notification | (none) |
| Art.30 | Notification procedure | (none) |
| Art.31 | Requirements relating to notified bodies | (none) |
| Art.32 | Presumption of conformity with requirements relating to notified bodies | (none) |
| Art.33 | Subsidiaries of notified bodies and subcontracting | (none) |
| Art.34 | Operational obligations of notified bodies | (none) |
| Art.35 | Identification numbers and lists of notified bodies | (none) |
| Art.36 | Changes to notifications | (none) |
| Art.37 | Challenge to the competence of notified bodies | (none) |
| Art.38 | Coordination of notified bodies | (none) |
| Art.39 | Conformity assessment bodies of third countries | (none) |
| Art.40 | Harmonised standards and standardisation deliverables | (none) |
| Art.41 | Common specifications | (none) |
| Art.42 | Presumption of conformity with certain requirements | (none) |
| Art.43 | Conformity assessment | `ai_act_data.high_risk_ai_categories` |
| Art.44 | Certificates | `ai_act_data.high_risk_ai_categories` |
| Art.45 | Extraordinary functioning of notified bodies | (none) |
| Art.46 | Derogation from conformity assessment procedure | (none) |
| Art.47 | EU declaration of conformity | `ai_act_data.ai_role` |
| Art.48 | CE marking of conformity | `ai_act_data.ai_role` |
| Art.49 | Registration | `ai_act_data.high_risk_ai_categories` |
| Art.50 | Transparency obligations for certain AI systems | `ai_act_data.uses_ai` |
| Art.51 | Classification of general-purpose AI models as models with systemic risk | `ai_act_data.uses_gpai` |
| Art.52 | Procedure | `ai_act_data.uses_gpai` |
| Art.53 | Obligations for providers of general-purpose AI models | `ai_act_data.uses_gpai` |
| Art.54 | Authorised representatives of providers of general-purpose AI models | `ai_act_data.uses_gpai` |
| Art.55 | Obligations for providers of general-purpose AI models with systemic risk | (none) |
| Art.56 | Codes of practice | (none) |
| Art.57 | AI regulatory sandboxes | (none) |
| Art.58 | Detailed arrangements for AI regulatory sandboxes | (none) |
| Art.59 | Further processing of personal data for AI in public interest in regulatory sandbox | (none) |
| Art.60 | Testing of high-risk AI systems in real world conditions | (none) |
| Art.61 | Informed consent to participate in testing | `company_size` |
| Art.62 | Measures for providers and deployers, in particular SMEs | (none) |
| Art.63 | Derogations for specific operators | `company_size` |
| Art.64 | AI Office | `ai_act_data.high_risk_ai_categories` |
| Art.65 | Establishment and structure of the European Artificial Intelligence Board | (none) |
| Art.66 | Tasks of the Board | (none) |
| Art.67 | Advisory forum | (none) |
| Art.68 | Scientific panel of independent experts | (none) |
| Art.69 | Access to the pool of experts by the Member States | `ai_act_data.high_risk_ai_categories` |
| Art.70 | National competent authorities | (none) |
| Art.71 | EU database for high-risk AI systems | `ai_act_data.high_risk_ai_categories` |
| Art.72 | Post-market monitoring by providers | `ai_act_data.high_risk_ai_categories` |
| Art.73 | Reporting of serious incidents by providers | `ai_act_data.high_risk_ai_categories` |
| Art.74 | Market surveillance activities | (none) |
| Art.75 | Mutual assistance, market surveillance | (none) |
| Art.76 | Oversight of testing in real world conditions | (none) |
| Art.77 | Powers of authorities protecting fundamental rights | `ai_act_data.ai_role` |
| Art.78 | Confidentiality | (none) |
| Art.79 | Procedure at national level for dealing with AI systems presenting a risk | (none) |
| Art.80 | Procedure for dealing with AI systems classified as non-high-risk | `ai_act_data.uses_gpai` |
| Art.81 | Union safeguard procedure | (none) |
| Art.82 | Compliant AI systems which present a risk | (none) |
| Art.83 | Formal non-compliance | (none) |
| Art.84 | Union AI testing support structures | (none) |
| Art.85 | Right to lodge a complaint with a market surveillance authority | (none) |
| Art.86 | Right to explanation | `ai_act_data.high_risk_ai_categories` |
| Art.87 | Reporting of breaches and protection of reporting persons | (none) |
| Art.88 | Enforcement of the obligations of providers of general-purpose AI models | (none) |
| Art.89 | Monitoring actions | (none) |
| Art.90 | Alerts of systemic risks by the scientific panel | (none) |
| Art.91 | Power to request documentation and information | (none) |
| Art.92 | Power to conduct evaluations | (none) |
| Art.93 | Power to request measures | (none) |
| Art.94 | Procedural rights of economic operators | (none) |
| Art.95 | Codes of conduct for voluntary application | (none) |
| Art.96 | Guidelines from the Commission | (none) |
| Art.97 | Exercise of the delegation | (none) |
| Art.98 | Committee procedure | (none) |
| Art.99 | Penalties | (none) |
| Art.100 | Administrative fines on Union institutions | (none) |
| Art.101 | Fines for providers of general-purpose AI models | (none) |
| Art.102 | Amendment to Regulation (EC) No 300/2008 | (none) |
| Art.103 | Amendment to Regulation (EU) No 167/2013 | (none) |
| Art.104 | Amendment to Regulation (EU) No 168/2013 | (none) |
| Art.105 | Amendment to Directive 2014/90/EU | (none) |
| Art.106 | Amendment to Directive (EU) 2016/797 | (none) |
| Art.107 | Amendment to Regulation (EU) 2018/858 | `industry` |
| Art.108 | Amendments to Regulation (EU) 2018/1139 | `industry` |
| Art.109 | Amendment to Regulation (EU) 2019/2144 | `ai_act_data.uses_ai` |
| Art.110 | Amendment to Directive (EU) 2020/1828 | (none) |
| Art.111 | AI systems already placed on the market | (none) |
| Art.112 | Evaluation and review | `ai_act_data.uses_ai` |
| Art.113 | Entry into force and application | (none) |
