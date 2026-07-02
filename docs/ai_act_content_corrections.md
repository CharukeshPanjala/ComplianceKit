# EU AI Act Content Corrections

Source of truth: `docs/Ai_act.pdf` (Regulation EU 2024/1689, official text), cross-referenced article by article using `pdftotext -layout` extraction and the operative article headers (e.g. "Article 32" on its own line, followed by the article title) found at the following line numbers in the extracted text: Art.32 (4922), Art.33 (4933), Art.34 (4951), Art.35 (4970), Art.36 (4982), Art.37 (5091), Art.38 (5117), Art.39 (5135), Art.40 (5149), Art.41 (5185), Art.42 (5255), Art.46 (5422), Art.51 (5651), Art.52 (5674), Art.53 (5727), Art.54 (5795), Art.55 (5853), Art.56 (5888), Art.61 (6368), Art.62 (6397), Art.63 (6435), Art.64 (6461), Art.65 (6470), Art.66 (6520), Art.67 (6599), Art.68 (6639), Art.69 (6698), Art.70 (6720), Art.77 (7116), Art.78 (7146), Art.79 (7210), Art.80 (7287), Art.81 (7328), Art.82 (7354), Art.83 (7388), Art.84 (7424), Art.85 (7443), Art.88 (7486), Art.89 (7500), Art.90 (7520), Art.91 (7544), Art.92 (7575), Art.93 (7623), Art.94 (7648), Art.99 (7799), Art.100 (7892), Art.101 (7947), Art.102 (7993), Art.103 (8012), Art.104 (8030), Art.105 (8050), Art.106 (8071), Art.107 (8093), Art.108 (8111), Art.109 (8164), Art.110 (8182), Art.111 (8195), Art.112 (8223).

This file covers the 44 articles flagged MISMATCH in `docs/article_audit_ai_act.md`, plus the missing real Article 54 (insert). Per the audit, only these 44 article numbers in the DB are MISMATCH; surrounding articles in the same chapters (e.g. 28-31, 40-45, 51, 57-60, 70, 72-76, 78, 86, 87, 95-98, 113) are MATCH or PARTIAL and are not included here.

All `plain_english` text below follows house style: no em dashes, customer-facing plain language.

---

## Article 32

**Current (wrong) title:** Subsidiaries of and subcontracting by notified bodies
**Current (wrong) description (truncated to ~2 sentences):** Where a notified body subcontracts specific conformity assessment tasks or uses a subsidiary, it shall ensure that the subcontractor or subsidiary meets the requirements and shall inform the notifying authority. Notified bodies shall take full responsibility...

**Corrected title:** Presumption of conformity with requirements relating to notified bodies
**Corrected description (full, from the real Regulation text):** Where a conformity assessment body demonstrates its conformity with the criteria laid down in the relevant harmonised standards or parts thereof, the references of which have been published in the Official Journal of the European Union, it shall be presumed to comply with the requirements set out in Article 31 in so far as the applicable harmonised standards cover those requirements.
**Corrected plain_english:** If a conformity assessment body meets the published EU harmonised standards covering notified body requirements, it is automatically presumed to meet those requirements without separate proof.

**Notes:** The DB's current Article 32 content is actually real Article 33's content ("Subsidiaries of notified bodies and subcontracting"). That correct content should move to Article 33 below. Other fields unchanged unless noted at Article 33.

---

## Article 33

**Current (wrong) title:** Operational obligations of notified bodies
**Current (wrong) description (truncated to ~2 sentences):** Notified bodies shall carry out conformity assessments in accordance with the conformity assessment procedures. They shall carry out their tasks with proportionate administrative burden, avoid unnecessary obstacles, take into account specific interests...

**Corrected title:** Subsidiaries of notified bodies and subcontracting
**Corrected description (full, from the real Regulation text):** Where a notified body subcontracts specific tasks connected with the conformity assessment or has recourse to a subsidiary, it shall ensure that the subcontractor or the subsidiary meets the requirements laid down in Article 31, and shall inform the notifying authority accordingly. Notified bodies shall take full responsibility for the tasks performed by any subcontractors or subsidiaries. Activities may be subcontracted or carried out by a subsidiary only with the agreement of the provider, and notified bodies shall make a list of their subsidiaries publicly available. The relevant documents concerning the assessment of the qualifications of the subcontractor or subsidiary, and the work carried out by them, shall be kept at the disposal of the notifying authority for five years from the termination of the subcontracting.
**Corrected plain_english:** A notified body that subcontracts work or uses a subsidiary must ensure that party meets the same requirements, take full responsibility for their work, get the provider's agreement first, and keep records available for 5 years.

**Notes:** This is the content currently mislabeled as Article 32 in the DB (one-article title drift, content was correct just under the wrong number). Other fields unchanged.

---

## Article 34

**Current (wrong) title:** Identification numbers and lists of notified bodies
**Current (wrong) description (truncated to ~2 sentences):** The Commission shall assign identification numbers to notified bodies and establish and maintain a publicly available list of notified bodies including their identification numbers and activities. The Commission shall ensure the list is kept up to date.

**Corrected title:** Operational obligations of notified bodies
**Corrected description (full, from the real Regulation text):** Notified bodies shall verify the conformity of high-risk AI systems in accordance with the conformity assessment procedures set out in Article 43. They shall avoid unnecessary burdens for providers, taking due account of provider size, sector, structure and the complexity of the system concerned, in particular to minimise administrative burdens and compliance costs for micro and small enterprises, while still respecting the required degree of rigour and level of protection. Notified bodies shall make available and submit, upon request, all relevant documentation, including the provider's documentation, to the notifying authority to allow it to conduct its assessment, designation, notification and monitoring activities.
**Corrected plain_english:** Notified bodies must assess high-risk AI systems against the proper conformity procedures, keep the burden proportionate for small businesses, and give the notifying authority access to all relevant documentation on request.

**Notes:** One-article title drift cascade continues; this is the content currently mislabeled as Article 33. Other fields unchanged.

---

## Article 35

**Current (wrong) title:** Changes to notifications
**Current (wrong) description (truncated to ~2 sentences):** Where a notifying authority has ascertained that a notified body no longer meets the notification requirements or is failing to fulfil its obligations, the notifying authority shall restrict, suspend or withdraw the notification as appropriate. The Commission shall...

**Corrected title:** Identification numbers and lists of notified bodies
**Corrected description (full, from the real Regulation text):** The Commission shall assign a single identification number to each notified body, even where a body is notified under more than one Union act. The Commission shall make publicly available the list of bodies notified under this Regulation, including their identification numbers and the activities for which they have been notified, and shall ensure that list is kept up to date.
**Corrected plain_english:** Every notified body gets one identification number from the Commission, and the full public list of notified bodies (with their numbers and activities) is kept current.

**Notes:** Cascade continues; this is the content currently mislabeled as Article 34. Other fields unchanged.

---

## Article 36

**Current (wrong) title:** Challenge to the competence of notified bodies
**Current (wrong) description (truncated to ~2 sentences):** The Commission may investigate whether a notified body meets or continues to meet its notification requirements. The notifying authority shall provide the Commission with all relevant information on request. The Commission shall keep the results of such...

**Corrected title:** Changes to notifications
**Corrected description (full, from the real Regulation text):** The notifying authority shall notify the Commission and other Member States of any relevant changes to a notified body's notification. Extensions of scope follow the Articles 29-30 procedure; other changes follow a separate procedure. If a notified body ceases its conformity assessment activities, it must inform the notifying authority and affected providers, generally at least one year before a planned cessation; its certificates may remain valid for up to nine months if another notified body confirms it will assume responsibility. Where a notifying authority has sufficient reason to consider a notified body no longer meets the Article 31 requirements or is failing its obligations, it shall investigate without delay, give the body the chance to respond, and restrict, suspend or withdraw the designation as appropriate, informing the Commission and other Member States. The Article also sets out detailed rules on the validity of certificates following suspension, restriction or withdrawal of a notified body's designation, including conditions under which certificates remain valid for three to twelve months.
**Corrected plain_english:** If a notified body changes, stops operating, or no longer meets the requirements, strict notification and transition rules apply to protect the validity of certificates already issued, with timelines ranging from a few days to twelve months depending on the situation.

**Notes:** Cascade continues; this is the content currently mislabeled as Article 35. This is the longest article in the notified-bodies block (9 paragraphs in the real text); description above is condensed but legally faithful. Other fields unchanged.

---

## Article 37

**Current (wrong) title:** Coordination of notified bodies
**Current (wrong) description (truncated to ~2 sentences):** The Commission shall ensure appropriate coordination and cooperation between notified bodies active in the conformity assessment procedures for AI systems. Notified bodies shall participate in such coordination activities. The Commission may establish...

**Corrected title:** Challenge to the competence of notified bodies
**Corrected description (full, from the real Regulation text):** The Commission shall, where necessary, investigate all cases where there are reasons to doubt the competence of a notified body or its continued fulfilment of the Article 31 requirements and its applicable responsibilities. The notifying authority shall provide the Commission, on request, with all relevant information. The Commission shall keep all sensitive information obtained confidential in accordance with Article 78. Where the Commission ascertains that a notified body does not meet or no longer meets the requirements for its notification, it shall inform the notifying Member State and request corrective measures, including suspension or withdrawal of notification if necessary; if the Member State fails to act, the Commission may, by implementing act, suspend, restrict or withdraw the designation itself.
**Corrected plain_english:** The Commission can investigate any notified body suspected of no longer meeting the requirements, and if the Member State does not fix the problem, the Commission can suspend, restrict or withdraw that body's status itself.

**Notes:** Cascade continues; this is the content currently mislabeled as Article 36. Other fields unchanged.

---

## Article 38

**Current (wrong) title:** Conformity assessment bodies under the Cybersecurity Act
**Current (wrong) description (truncated to ~2 sentences):** Where a conformity assessment body has been accredited under the Cybersecurity Act (EU) 2019/881 to assess the conformity of cybersecurity requirements, that body may also be notified under this Regulation for AI conformity assessments where they demonstrate competence in AI systems. Dual accreditation can reduce compliance burden.

**Corrected title:** Coordination of notified bodies
**Corrected description (full, from the real Regulation text):** The Commission shall ensure appropriate coordination and cooperation between notified bodies active in conformity assessment procedures under this Regulation, operating through a sectoral group of notified bodies. Each notifying authority shall ensure its notified bodies participate in this group, directly or through designated representatives. The Commission shall provide for the exchange of knowledge and best practices between notifying authorities.
**Corrected plain_english:** Notified bodies coordinate with each other through a dedicated sector group set up and supported by the Commission, so practices stay consistent across the EU.

**Notes:** Cascade continues; this is the content currently mislabeled as Article 37. Real Article 38's topic ("Coordination of notified bodies") had been pushed down to the DB's "Article 39" slot incorrectly described as fabricated. Other fields unchanged.

---

## Article 39

**Current (wrong) title:** Conformity assessment bodies in third countries
**Current (wrong) description (truncated to ~2 sentences):** Conformity assessment bodies established in third countries may be authorised to carry out conformity assessment activities under this Regulation on the basis of bilateral agreements between the Union and the third country concerned. Such agreements shall provide for conditions equivalent to those applicable to notified bodies established in the Union.

**Corrected title:** Conformity assessment bodies of third countries
**Corrected description (full, from the real Regulation text):** Conformity assessment bodies established under the law of a third country with which the Union has concluded an agreement may be authorised to carry out the activities of notified bodies under this Regulation, provided that they meet the requirements laid down in Article 31 or ensure an equivalent level of compliance.
**Corrected plain_english:** Conformity assessment bodies based outside the EU can act as notified bodies only if the EU has an agreement with that country and the body meets equivalent standards to EU notified bodies.

**Notes:** The DB's existing title and content for "Article 39" were already substantively correct and match the real Article 39 almost word for word (audit had flagged this row PARTIAL, not MISMATCH, for numbering proximity reasons). Minor wording tightened to track the official text exactly ("Conformity assessment bodies of third countries", singular "of" not "in"). Other fields unchanged. Note: the audit doc's MISMATCH list technically includes Art.38 but treats Art.39 as PARTIAL; included here for completeness of the notified-bodies cascade since its title needed a small correction.

---

## Article 46

**Current (wrong) title:** Appeal against decisions of notified bodies
**Current (wrong) description (truncated to ~2 sentences):** Member States shall ensure that an appeal procedure against decisions of notified bodies is available. The appeal procedure shall be effective and accessible to all interested parties.

**Corrected title:** Derogation from conformity assessment procedure
**Corrected description (full, from the real Regulation text):** By way of derogation from Article 43, and upon a duly justified request, a market surveillance authority may authorise the placing on the market or putting into service of specific high-risk AI systems within its Member State for exceptional reasons of public security, protection of life and health, environmental protection, or protection of key industrial and infrastructural assets, for a limited period while the necessary conformity assessment is carried out. In a duly justified situation of urgency, law-enforcement or civil protection authorities may put a high-risk AI system into service without prior authorisation, provided authorisation is requested without undue delay during or after use; if refused, use must stop immediately and all outputs must be discarded. Authorisation is issued only if the authority concludes the system complies with Chapter III Section 2 requirements, and other Member States and the Commission are informed; if no objection is raised within 15 days, the authorisation is deemed justified, otherwise the Commission may enter consultations and decide whether it is justified.
**Corrected plain_english:** In genuine emergencies (public security, health, life-safety, critical infrastructure), a market surveillance authority can let a high-risk AI system go into use before the full conformity assessment is finished, but only temporarily and under strict conditions, and the EU can later overrule that approval if it disagrees.

**Notes:** The DB's title field said "Appeal against decisions of notified bodies" but its own description content was already about derogation, not appeals. The audit doc itself notes some confusion in identifying which is the "real" Article 46 title; on direct PDF verification the actual Article 46 header reads "Derogation from conformity assessment procedure," confirmed at line 5422 of the extracted text. There is no standalone "Appeal against decisions of notified bodies" article anywhere in the real Regulation; that topic does not appear as its own article. The corrected description above replaces the DB's one-sentence placeholder with the real, much more detailed legal content.

---

## Article 52

**Current (wrong) title:** Obligations for providers of general-purpose AI models
**Current (wrong) description (truncated to ~2 sentences):** Providers of general-purpose AI models shall: draw up and maintain technical documentation including training process, evaluation results, and capabilities; provide information and documentation to downstream AI system providers; establish a policy to...

**Corrected title:** Procedure
**Corrected description (full, from the real Regulation text):** Where a general-purpose AI model meets the high-impact-capability condition of Article 51(1)(a), the provider shall notify the Commission without delay, within two weeks of the requirement being met or becoming known, including information demonstrating that the requirement has been met. The provider may submit substantiated arguments that, despite meeting the condition, the model does not present systemic risk due to its specific characteristics and should not be so classified. If the Commission finds those arguments insufficient, it rejects them and the model is classified as presenting systemic risk. The Commission may also designate a model as presenting systemic risk ex officio or following a qualified alert from the scientific panel, based on the Annex XIII criteria, and is empowered to amend Annex XIII by delegated act. The Commission shall publish and maintain an up-to-date list of general-purpose AI models with systemic risk.
**Corrected plain_english:** If your general-purpose AI model crosses the systemic-risk threshold, you must notify the Commission within two weeks. You can argue your model is an exception, but if the Commission disagrees, it gets formally classified as systemic risk and added to a public list.

**Notes:** Real Article 52 is "Procedure," the Commission notification process for the systemic-risk threshold, not the GPAI provider obligations content. The real GPAI provider obligations (currently mislabeled "Article 52" in the DB) belong at Article 53, see below. This is the start of the GPAI cascade caused by real Article 54 being entirely missing from the DB (see Article 54 entry below for full explanation).

---

## Article 53

**Current (wrong) title:** Obligations for providers of general-purpose AI models with systemic risk
**Current (wrong) description (truncated to ~2 sentences):** In addition to Article 52 obligations, providers of GPAI models with systemic risk shall: perform model evaluations following state of the art protocols; assess and mitigate systemic risks; report serious incidents and corrective measures to the AI Office...

**Corrected title:** Obligations for providers of general-purpose AI models
**Corrected description (full, from the real Regulation text):** Providers of general-purpose AI models shall: (a) draw up and keep up to date technical documentation of the model, including its training and testing process and evaluation results, containing at minimum the Annex XI information, for provision on request to the AI Office and national competent authorities; (b) draw up, keep up to date and make available information and documentation to providers of AI systems intending to integrate the model, sufficient for them to understand the model's capabilities and limitations and comply with their own obligations, containing at minimum the Annex XII elements; (c) put in place a policy to comply with EU copyright law, including identifying and complying with rights reservations under Article 4(3) of Directive (EU) 2019/790; (d) draw up and make publicly available a sufficiently detailed summary of the content used to train the model, using an AI Office template. Obligations (a) and (b) do not apply to providers of free and open-source models that make their parameters, weights, architecture and usage information publicly available, unless the model presents systemic risk. Providers shall cooperate with the Commission and national competent authorities, and may rely on codes of practice under Article 56 to demonstrate compliance pending harmonised standards.
**Corrected plain_english:** If you provide a general-purpose AI model, you must keep technical documentation up to date, give downstream AI developers enough information to use your model safely, have a policy respecting copyright opt-outs for training data, and publish a summary of what you trained on. Open-source models with public weights are exempt from some of this, unless they carry systemic risk.

**Notes:** This is the content currently mislabeled as Article 52. Part of the GPAI cascade from the missing real Article 54.

---

## Article 54

**Current (wrong) title:** Codes of practice
**Current (wrong) description (truncated to ~2 sentences):** The AI Office shall facilitate the drawing up of codes of practice at Union level to contribute to the proper application of obligations for GPAI model providers. Participation in codes of practice is voluntary but creates presumption of conformity...

**Corrected title:** Authorised representatives of providers of general-purpose AI models
**Corrected description (full, from the real Regulation text):** Prior to placing a general-purpose AI model on the EU market, a provider established in a third country shall, by written mandate, appoint an authorised representative established in the Union. The provider shall enable the representative to perform the mandated tasks, which include: verifying the Annex XI technical documentation has been drawn up and Article 53 (and, where applicable, Article 55) obligations fulfilled; keeping a copy of the technical documentation available to the AI Office and national competent authorities for 10 years after the model is placed on the market, along with the provider's contact details; providing the AI Office with information and documentation on reasoned request; and cooperating with the AI Office and competent authorities on any action relating to the model. The mandate empowers the representative to be addressed by the AI Office or competent authorities instead of, or in addition to, the provider. The representative shall terminate the mandate if it has reason to believe the provider is acting contrary to its obligations, and must immediately inform the AI Office. This obligation does not apply to providers of free and open-source models meeting the openness criteria in Article 53(2), unless the model presents systemic risk.
**Corrected plain_english:** If you provide a general-purpose AI model from outside the EU, you must appoint an EU-based authorised representative before placing it on the market. That representative checks your documentation, holds it for 10 years, and answers to EU regulators on your behalf.

**Notes:** NEW ARTICLE TO INSERT. Real Article 54, "Authorised representatives of providers of general-purpose AI models," does not exist under any article number in the current 113-article database. This is the root cause of the entire GPAI block cascade: the DB currently has 113 articles total but is missing this one, so every subsequent GPAI-related article (53 through 56 in the real text) has been shifted one number earlier in the DB (DB 52 = real 53, DB 53 = real 55, DB 54 = real 56, etc.), and the DB invented an "Article 55" ("Other measures in support of innovation") that does not correspond to any real article at all. Inserting this article restores the correct numbering for 55 and 56 immediately following. Suggested fields for the new row: `chapter: "Chapter V — General-Purpose AI Models"`, `category: "GPAI"`, `severity: HIGH`, `is_mandatory: true`, `check_type: "profile_field"`, `profile_field: "ai_act_data.uses_gpai"` (paired with a non-EU establishment check once that data point exists), `applicability_tags: ["EU_AI_ACT", "GPAI", "authorised_representative", "third_country"]`. These are recommendations only; final field values need product/engineering sign-off since this is a net-new row, not a one-to-one text correction.

---

## Article 55

**Current (wrong) title:** Other measures in support of innovation for providers of GPAI models
**Current (wrong) description (truncated to ~2 sentences):** The AI Office shall provide GPAI model providers with technical tools and guidance on how to comply with obligations. The AI Office shall develop standardised templates and model cards for GPAI documentation. ENISA shall provide cybersecurity guidance...

**Corrected title:** Obligations for providers of general-purpose AI models with systemic risk
**Corrected description (full, from the real Regulation text):** In addition to the Articles 53 and 54 obligations, providers of general-purpose AI models with systemic risk shall: (a) perform model evaluation using standardised, state-of-the-art protocols and tools, including adversarial testing, to identify and mitigate systemic risks; (b) assess and mitigate possible systemic risks at Union level, including their sources; (c) track, document and report without undue delay to the AI Office and, as appropriate, national competent authorities, relevant information about serious incidents and possible corrective measures; (d) ensure an adequate level of cybersecurity protection for the model and its physical infrastructure. Providers may rely on codes of practice under Article 56 to demonstrate compliance pending harmonised standards.
**Corrected plain_english:** If your general-purpose AI model is classified as carrying systemic risk, on top of the standard GPAI obligations you must run adversarial testing, actively manage systemic risks, report serious incidents promptly, and secure the model and its infrastructure to a high cybersecurity standard.

**Notes:** This is the content currently mislabeled as Article 53. The DB's existing "Article 55" content (AI Office innovation-support measures) does not correspond to any real article in this part of the Regulation and should be removed once this correction is applied; it appears to be an invented placeholder. Part of the GPAI cascade.

---

## Article 56

**Current (wrong) title:** Qualitative description of parameters relevant for classification
**Current (wrong) description (truncated to ~2 sentences):** The Commission is empowered to adopt delegated acts to specify criteria and processes for determining systemic risk for GPAI models, including updating the FLOPs threshold in light of technological developments, and establishing criteria for assessing...

**Corrected title:** Codes of practice
**Corrected description (full, from the real Regulation text):** The AI Office shall encourage and facilitate the drawing up of codes of practice at Union level to support proper application of this Regulation, taking into account international approaches. The AI Office and the Board shall aim to ensure codes of practice cover at least the Articles 53 and 55 obligations, including: keeping required information up to date; the level of detail for training-content summaries; identifying the type and nature of systemic risks; and the measures and procedures for assessing and managing those risks. The AI Office may invite providers, national authorities, civil society, industry, academia and other stakeholders to participate. Codes shall set clear objectives and commitments with key performance indicators, and participants shall report regularly on implementation. The Commission may, by implementing act, give an approved code of practice general validity across the Union. Codes were to be ready by 2 May 2025; if not finalised or deemed inadequate by 2 August 2025, the Commission may instead set common rules for the same obligations by implementing act.
**Corrected plain_english:** The EU AI Office runs a voluntary code-of-practice process that lets general-purpose AI model providers demonstrate compliance with their core obligations before official technical standards exist. If the industry can't agree a workable code in time, the Commission can step in and set the rules directly instead.

**Notes:** The DB's existing "Article 56" content (Annex XIII FLOPs/parameter criteria) is real Annex XIII material, not Article 56 text, and should be removed or relabeled as Annex content rather than an article. Part of the GPAI cascade; this is the final article in the GPAI block, after which Chapter VI (Innovation Support, Article 57 onward) begins correctly in the DB.

---

## Article 61

**Current (wrong) title:** Measures for providers and deployers, in particular SMEs including start-ups
**Current (wrong) description (truncated to ~2 sentences):** Member States shall take measures to support SMEs and start-ups including: priority access to AI regulatory sandboxes; dedicated channels for communication with competent authorities; reduced fees for conformity assessments; technical support and training...

**Corrected title:** Informed consent to participate in testing in real world conditions outside AI regulatory sandboxes
**Corrected description (full, from the real Regulation text):** For testing in real-world conditions under Article 60, freely given informed consent must be obtained from test subjects before they participate, after they have been clearly informed about: the nature, objectives, and possible inconvenience of the testing; the conditions and expected duration of participation; their rights, including the right to refuse or withdraw at any time without detriment or justification; the arrangements for requesting reversal or disregard of the AI system's outputs; and the unique EU-wide identification number of the test plus contact details for further information. The informed consent shall be dated, documented, and a copy given to the subject or their legal representative.
**Corrected plain_english:** If your AI system is tested on real people outside a regulatory sandbox, you must get their clear, documented, freely given consent first, explaining what the test involves, their right to withdraw at any time, and how to contact you.

**Notes:** Real Article 61 is about informed consent for real-world testing, not SME support measures (that is real Article 62, see below). One-article title drift in this block.

---

## Article 62

**Current (wrong) title:** Mechanism to report concerns about AI systems
**Current (wrong) description (truncated to ~2 sentences):** Any person or entity may report to the relevant national competent authority any serious concern about a non-compliant AI system. Competent authorities shall ensure that reports can be made anonymously where appropriate. Whistleblower protections apply...

**Corrected title:** Measures for providers and deployers, in particular SMEs including start-ups
**Corrected description (full, from the real Regulation text):** Member States shall: give SMEs and start-ups priority access to AI regulatory sandboxes where they meet eligibility criteria; organise awareness and training activities tailored to SMEs, start-ups, deployers and local public authorities; provide dedicated communication channels for advice and queries; and facilitate SME participation in standardisation. SME conformity assessment fees shall be reduced proportionately to size and market presence. The AI Office shall provide standardised templates, maintain a single information platform, run awareness campaigns, and promote convergence of best practices in AI-related public procurement.
**Corrected plain_english:** EU Member States and the AI Office must actively support small businesses and start-ups complying with the AI Act: priority sandbox access, lower fees, dedicated help channels, and training.

**Notes:** This is the content currently mislabeled as Article 61. There is no standalone "Mechanism to report concerns about AI systems" article in the real Regulation; the closest related provision is the general complaints right at real Article 85 ("Right to lodge a complaint with a market surveillance authority"), which is itself separately mismatched in the DB (see Article 85 entry below). The DB's current Article 62 content appears to be either fabricated or conflated with Article 85's topic.

---

## Article 64

**Current (wrong) title:** Access to data and documentation
**Current (wrong) description (truncated to ~2 sentences):** National competent authorities shall be granted access to the training, validation and testing datasets used for high-risk AI systems, where necessary and proportionate for the performance of their tasks. Providers shall establish national contact points...

**Corrected title:** AI Office
**Corrected description (full, from the real Regulation text):** The Commission shall develop Union expertise and capabilities in the field of AI through the AI Office. Member States shall facilitate the tasks entrusted to the AI Office as reflected in this Regulation.
**Corrected plain_english:** The European Commission runs a dedicated AI Office to build EU-wide AI expertise, and Member States must support its work.

**Notes:** This is the start of the most severe content-substitution zone identified in the audit (Articles 64-70 in the DB describe market-surveillance/incident/penalty content that actually belongs many articles later in the real text). Real Article 64 is a short, purely institutional article establishing the AI Office; it has no customer-actionable content and no legitimate profile_field. The DB's dangling `ai_act_data.high_risk_categories` reference on this row should be removed entirely (not just renamed) since the corrected article has `check_type: informational`.

---

## Article 65

**Current (wrong) title:** Market surveillance and control of AI systems in the Union market
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) 2019/1020 on market surveillance shall apply to AI systems covered by this Regulation. Competent authorities shall conduct market surveillance activities, investigate suspected non-compliance, and take corrective measures. Market surveillance...

**Corrected title:** Establishment and structure of the European Artificial Intelligence Board
**Corrected description (full, from the real Regulation text):** A European Artificial Intelligence Board ("the Board") is established, composed of one representative per Member State, with the European Data Protection Supervisor as an observer and the AI Office attending without voting rights. Representatives are designated for renewable three-year terms and must have the competence and authority to contribute to the Board's tasks, act as single points of contact, and facilitate national coordination. The Board adopts its own rules of procedure by two-thirds majority, establishes standing sub-groups for market surveillance and notified bodies, may create further sub-groups as needed, and is chaired by one of the Member State representatives, with the AI Office providing the secretariat.
**Corrected plain_english:** A European AI Board made up of one representative per EU country coordinates how the AI Act is applied consistently across the Union, supported administratively by the AI Office.

**Notes:** The DB's current Article 65 content (market surveillance / Regulation 2019/1020) is actually real Article 74's content; see that entry below. No legitimate profile_field for the corrected institutional content.

---

## Article 66

**Current (wrong) title:** Procedure for dealing with AI systems presenting a risk at national level
**Current (wrong) description (truncated to ~2 sentences):** Where a competent authority finds that an AI system presents a risk, it shall carry out an evaluation and require the provider to take appropriate corrective actions within a specified period. Where the provider does not take corrective actions, the...

**Corrected title:** Tasks of the Board
**Corrected description (full, from the real Regulation text):** The Board advises and assists the Commission and Member States to facilitate consistent and effective application of this Regulation. Its tasks include: coordinating among national competent authorities; collecting and sharing technical and regulatory expertise and best practice; advising on implementation, particularly GPAI enforcement; harmonising administrative practices, including for derogations, sandboxes and real-world testing; issuing recommendations and opinions, including on codes of conduct, the Article 112 review, technical specifications, harmonised standards, AI uptake trends and value-chain developments; supporting AI literacy and public awareness; facilitating common criteria and benchmarks; cooperating with other EU bodies in product safety, cybersecurity, competition, financial services and data protection; supporting international cooperation; assisting national authorities and the Commission in building expertise; supporting regulatory sandboxes; and advising on qualified alerts regarding general-purpose AI models.
**Corrected plain_english:** The European AI Board's job is to keep AI Act enforcement consistent across the EU: sharing best practice, advising regulators and the Commission, and supporting training and cooperation between countries.

**Notes:** The DB's current Article 66 content (procedure for risky AI systems at national level) is actually real Article 79's content; see that entry below. No legitimate profile_field for the corrected institutional content.

---

## Article 67

**Current (wrong) title:** Procedure for dealing with compliant high-risk AI systems that present a risk
**Current (wrong) description (truncated to ~2 sentences):** Where a competent authority finds that a compliant high-risk AI system nevertheless presents a risk to health, safety, or fundamental rights, it shall require the provider to take appropriate measures or shall restrict or prohibit the making available...

**Corrected title:** Advisory forum
**Corrected description (full, from the real Regulation text):** An advisory forum is established to provide technical expertise and advise the Board and Commission. Its membership balances stakeholders including industry, start-ups, SMEs, civil society and academia, and must be balanced between commercial and non-commercial interests. The Commission appoints members for two-year terms (extendable up to four more years). The Fundamental Rights Agency, ENISA, CEN, CENELEC and ETSI are permanent members. The forum sets its own rules of procedure, elects two co-chairs for renewable two-year terms, meets at least twice a year, may invite experts, may prepare opinions at the Board's or Commission's request, may establish sub-groups, and must publish an annual activity report.
**Corrected plain_english:** An advisory forum of industry, civil society, and academic experts feeds technical input to the European AI Board and the Commission, meeting at least twice a year.

**Notes:** The DB's current Article 67 content (procedure for compliant-but-risky systems) is actually real Article 82's content; see that entry below. No legitimate profile_field.

---

## Article 68

**Current (wrong) title:** Union safeguard procedure
**Current (wrong) description (truncated to ~2 sentences):** Where a Member State takes corrective action against an AI system, it shall inform the Commission and other Member States. Where the Commission considers the measure justified, it may adopt implementing acts extending the measure to the whole Union...

**Corrected title:** Scientific panel of independent experts
**Corrected description (full, from the real Regulation text):** The Commission shall, by implementing act, establish a scientific panel of independent experts to support enforcement, selected for up-to-date AI expertise, independence from any AI provider, and ability to act diligently and objectively, with fair gender and geographic representation. The panel advises and supports the AI Office, in particular by alerting it to possible systemic risks of general-purpose AI models, contributing to evaluation tools and benchmarks, advising on systemic-risk classification, supporting market surveillance authorities and cross-border activities, and supporting the Union safeguard procedure under Article 81. Panel experts must act impartially, keep information confidential, and declare any conflicts of interest, which the AI Office must actively manage.
**Corrected plain_english:** A panel of independent AI experts, vetted for expertise and independence, advises the EU's AI Office on technical questions like whether a general-purpose AI model poses systemic risk.

**Notes:** The DB's current Article 68 content (Union safeguard procedure) is actually real Article 81's content; see that entry below. No legitimate profile_field.

---

## Article 69

**Current (wrong) title:** Reporting of serious incidents
**Current (wrong) description (truncated to ~2 sentences):** Providers of high-risk AI systems placed on the EU market shall report any serious incident to the market surveillance authorities of the Member States in which the incident occurred. A serious incident is one that directly or indirectly leads to death...

**Corrected title:** Access to the pool of experts by the Member States
**Corrected description (full, from the real Regulation text):** Member States may call on the scientific panel's experts to support their own enforcement activities under this Regulation. Member States may be required to pay fees for that advice and support, with fee structure set out in the Article 68 implementing act, taking into account effective and cost-effective implementation and equal access for all Member States. The Commission shall facilitate timely access to experts and ensure efficient coordination with the Union AI testing support structures under Article 84.
**Corrected plain_english:** EU countries can call on the independent expert panel for help enforcing the AI Act, and the Commission makes sure access is fair and well-coordinated across all Member States.

**Notes:** The DB's current Article 69 content (serious-incident reporting) is actually real Article 73's content, which is itself already correctly present in the DB under its own Article 73 entry (the audit notes Article 73 is MATCH). This means the DB currently has serious-incident reporting duplicated, incorrectly, under Article 69 as well as correctly under Article 73. The corrected Article 69 content above has no customer-actionable data point and no legitimate profile_field; the dangling `ai_act_data.high_risk_categories` reference on this row should be removed.

---

## Article 77

**Current (wrong) title:** Obligations of deployers
**Current (wrong) description (truncated to ~2 sentences):** Where deployers identify serious incidents or malfunctions in high-risk AI systems, they shall immediately notify the provider and competent authorities. Deployers shall cooperate with providers and authorities in any investigation. Deployers shall preserve...

**Corrected title:** Powers of authorities protecting fundamental rights
**Corrected description (full, from the real Regulation text):** National public authorities or bodies that supervise or enforce fundamental rights obligations under Union law (including non-discrimination), in relation to high-risk AI systems listed in Annex III, have the power to request and access any documentation created or maintained under this Regulation, in accessible language and format, where necessary for their mandate; they must inform the relevant market surveillance authority of such requests. By 2 November 2024, each Member State must identify these authorities and publish the list, notifying the Commission and other Member States and keeping it current. If the documentation is insufficient to establish whether a fundamental-rights infringement occurred, the authority may make a reasoned request to the market surveillance authority to organise technical testing of the system, carried out with the requesting authority's close involvement. Information obtained under this Article must be treated confidentially per Article 78.
**Corrected plain_english:** National human-rights and equality bodies can demand to see your high-risk AI system's documentation, and even request technical testing of it, if they suspect it is breaching people's fundamental rights.

**Notes:** The DB's current Article 77 content ("Obligations of deployers") duplicates content already correctly covered at real Article 26, which the audit confirms is MATCH in the DB. Real Article 77 is a distinct article about fundamental-rights authorities' investigative powers, unrelated to deployer obligations. The dangling field references (`role`, `high_risk_categories`) on this DB row should be removed since the corrected content has no profile_field.

---

## Article 79

**Current (wrong) title:** Penalties
**Current (wrong) description (truncated to ~2 sentences):** Non-compliance with the prohibition of prohibited AI practices (Article 5): up to €35,000,000 or 7% of total worldwide annual turnover, whichever is higher. Non-compliance with high-risk AI requirements or GPAI obligations: up to €15,000,000 or 3% of total worldwide annual turnover, whichever is higher...

**Corrected title:** Procedure at national level for dealing with AI systems presenting a risk
**Corrected description (full, from the real Regulation text):** Where a market surveillance authority has sufficient reason to consider an AI system presents a risk to health, safety or fundamental rights (within the meaning of "product presenting a risk" in Regulation (EU) 2019/1020), it shall evaluate the system's compliance with all applicable requirements, giving particular attention to risks to vulnerable groups, and shall inform and cooperate with the relevant fundamental-rights authorities under Article 77 where relevant. Operators must cooperate. If non-compliance is found, the authority requires the operator to take corrective action, withdraw, or recall the system, generally within 15 working days. If non-compliance is not limited to the national territory, the Commission and other Member States are informed. If the operator does not act, the authority takes provisional measures to prohibit, restrict, withdraw or recall the system and notifies the Commission and other Member States, indicating whether non-compliance relates to prohibited practices (Article 5), high-risk requirements, harmonised standards shortcomings, or Article 50 transparency failures. Other market surveillance authorities have three months (or 30 days for Article 5 non-compliance) to object; absent objection, the measure is deemed justified.
**Corrected plain_english:** If a national regulator believes your AI system poses a risk, it investigates, and if it finds a problem, it can order you to fix, withdraw, or recall the system, usually within 15 working days, and may escalate EU-wide if you do not comply.

**Notes:** This is the most consequential mismatch identified in the audit: the DB currently has the EUR 35M/7% penalties content under Article 79's number, but real Article 79 has nothing to do with penalties; the actual penalties article is real Article 99 (see that entry below, where the correction restores the fines content to its proper number). The penalties content that was here should be moved to Article 99. No legitimate profile_field for the corrected content; remove dangling references if any exist on this row in the future fix.

---

## Article 80

**Current (wrong) title:** Penalties for providers of general-purpose AI models
**Current (wrong) description (truncated to ~2 sentences):** Where the AI Office finds that a provider of a GPAI model has infringed the requirements of this Regulation, it may impose fines of up to €15,000,000 or 3% of total worldwide annual turnover. Where a GPAI model provider fails to provide requested information...

**Corrected title:** Procedure for dealing with AI systems classified by the provider as non-high-risk in application of Annex III
**Corrected description (full, from the real Regulation text):** Where a market surveillance authority has sufficient reason to consider that an AI system the provider classified as non-high-risk under Article 6(3) is in fact high-risk, it shall evaluate the system's classification against the Article 6(3) conditions and Commission guidelines. If found high-risk, the authority requires the provider to bring the system into compliance and take corrective action within a set period; non-EU-wide non-compliance triggers notification to the Commission and other Member States. Providers who fail to bring the system into compliance, or who are found to have misclassified the system as non-high-risk specifically to avoid Chapter III Section 2 requirements, are subject to fines under Article 99. Market surveillance authorities may use the EU database (Article 71) to support their checks.
**Corrected plain_english:** If a regulator suspects you wrongly labelled your AI system as "not high-risk" to dodge the rules, it can investigate, and if you are found to have misclassified deliberately, you face fines under Article 99.

**Notes:** The DB's current Article 80 content (GPAI-specific penalties) is actually real Article 101's content; see that entry below where it is restored to its proper number. The real GPAI penalty cap per Article 101 is EUR 15M or 3% of worldwide turnover, matching what was misplaced here; that figure moves to the Article 101 entry. No legitimate profile_field for the corrected content (`ai_act_data.gpai_model` dangling reference should be removed, not renamed, since this row's correct subject does not concern GPAI at all).

---

## Article 81

**Current (wrong) title:** Procedural rules for the adoption of supervisory measures by the AI Office
**Current (wrong) description (truncated to ~2 sentences):** Before taking supervisory measures, the AI Office shall give the GPAI model provider the opportunity to submit observations. The AI Office shall take into account all relevant factors and ensure proportionality. Providers have the right to be heard before...

**Corrected title:** Union safeguard procedure
**Corrected description (full, from the real Regulation text):** Where, within three months of an Article 79(5) notification (30 days for Article 5 prohibited-practice non-compliance), another Member State's market surveillance authority objects to a measure, or the Commission considers it contrary to Union law, the Commission shall consult with the relevant Member State and operators and evaluate the measure, deciding within six months (60 days for Article 5 cases) whether it is justified, notifying the relevant authority and informing all others. If justified, all Member States must take appropriate restrictive measures against the system and inform the Commission; if unjustified, the Member State must withdraw the measure. Where the non-compliance stems from shortcomings in harmonised standards or common specifications, the Commission applies the Regulation (EU) No 1025/2012 Article 11 procedure.
**Corrected plain_english:** If EU countries disagree about whether a national AI enforcement action was justified, the European Commission steps in to make the final call, and if it agrees the action was right, every Member State must enforce it.

**Notes:** The DB's current Article 81 content ("Procedural rules for the adoption of supervisory measures by the AI Office," GPAI-provider-specific) does not correspond to any single real article checked in this audit; it appears to be a fabricated or loosely paraphrased composite, possibly drawing on elements of Articles 91-94 (AI Office powers over GPAI providers). No legitimate profile_field for the corrected content.

---

## Article 82

**Current (wrong) title:** Right to be heard and access to the file
**Current (wrong) description (truncated to ~2 sentences):** Before adopting a decision finding an infringement, the AI Office shall give the undertaking the opportunity to submit its observations. The undertaking shall have access to the file, subject to the legitimate interest of protecting professional secrets...

**Corrected title:** Compliant AI systems which present a risk
**Corrected description (full, from the real Regulation text):** Where, after an Article 79 evaluation and consultation with relevant fundamental-rights authorities, a market surveillance authority finds that a high-risk AI system complies with the Regulation but still presents a risk to health, safety, fundamental rights, or other public interests, it shall require the operator to take all appropriate measures to remove that risk within a prescribed period. The operator must ensure corrective action covers all affected systems placed on the market. Member States must immediately inform the Commission and other Member States of such findings, including identifying details, the nature of the risk, and the measures taken. The Commission shall consult with the Member States and operators concerned, evaluate the measures, decide whether they are justified, and communicate its decision.
**Corrected plain_english:** Even an AI system that technically complies with the AI Act can still be ordered to fix a risk it poses to health, safety, or rights, and the fix must apply to every copy of that system on the EU market.

**Notes:** The DB's current Article 82 content ("Right to be heard and access to the file," AI Office disciplinary procedure for GPAI providers) does not correspond to any single real article checked; it most closely echoes elements of real Article 94 ("Procedural rights of economic operators of the general-purpose AI model"), which is itself separately mismatched (see Article 94 entry below). No legitimate profile_field for the corrected content.

---

## Article 83

**Current (wrong) title:** Limitation periods for the imposition of penalties
**Current (wrong) description (truncated to ~2 sentences):** The limitation period for the imposition of penalties shall be 5 years from the date of the infringement. The limitation period for the enforcement of penalties shall be 5 years from the date of the decision imposing the fine. The limitation period shall...

**Corrected title:** Formal non-compliance
**Corrected description (full, from the real Regulation text):** Where a market surveillance authority finds that the CE marking has been affixed in violation of Article 48, or not affixed at all; the EU declaration of conformity under Article 47 has not been drawn up or not drawn up correctly; the EU database registration under Article 71 has not been carried out; no authorised representative has been appointed where required; or technical documentation is unavailable, it shall require the provider to end the non-compliance within a prescribed period. If the non-compliance persists, the authority shall take appropriate and proportionate measures to restrict or prohibit the system being made available, or ensure it is recalled or withdrawn without delay.
**Corrected plain_english:** Missing or incorrect CE marking, missing EU declaration of conformity, missing EU database registration, no authorised representative, or missing technical documentation are all treated as formal compliance failures, and the regulator can force you to fix them or pull the product from the market.

**Notes:** No "Limitation periods for the imposition of penalties" article exists at all in the real Regulation under Article 83 or anywhere checked in this audit; the DB's current content appears fabricated. Real Article 83 is "Formal non-compliance" as corrected above. No legitimate profile_field for the corrected content; the original DB row had `profile_field: None` already (limitation-period content was purely informational), so this remains unchanged at the field level, only title/description/plain_english change.

---

## Article 84

**Current (wrong) title:** Publication of decisions
**Current (wrong) description (truncated to ~2 sentences):** The AI Office shall publish all decisions finding infringements and fines imposed under this Regulation, after redacting commercially sensitive information. National competent authorities shall publish their decisions on market withdrawal, restriction...

**Corrected title:** Union AI testing support structures
**Corrected description (full, from the real Regulation text):** The Commission shall designate one or more Union AI testing support structures to perform the tasks under Article 21(6) of Regulation (EU) 2019/1020 in the AI field. These structures shall also provide independent technical or scientific advice at the request of the Board, the Commission, or market surveillance authorities.
**Corrected plain_english:** The EU sets up dedicated technical testing centres that regulators and the European AI Board can call on for independent expert advice and AI testing support.

**Notes:** No "Publication of decisions" article exists under Article 84 or elsewhere checked in the real Regulation; the DB's current content appears fabricated (there is no general public-decisions-register obligation of this kind in the text reviewed). No legitimate profile_field for the corrected content.

---

## Article 85

**Current (wrong) title:** European AI Office
**Current (wrong) description (truncated to ~2 sentences):** The Commission shall establish the European AI Office within its structures. The AI Office shall coordinate the implementation and enforcement of this Regulation, particularly for GPAI models. The AI Office shall develop tools for implementation, support...

**Corrected title:** Right to lodge a complaint with a market surveillance authority
**Corrected description (full, from the real Regulation text):** Without prejudice to other administrative or judicial remedies, any natural or legal person with grounds to believe this Regulation has been infringed may submit a complaint to the relevant market surveillance authority. Complaints shall be taken into account for market surveillance purposes and handled per the dedicated procedures established by the authority, in accordance with Regulation (EU) 2019/1020.
**Corrected plain_english:** Anyone, whether an individual or a company, who believes the AI Act has been breached can file a complaint with the relevant national market surveillance authority, and that authority must take it seriously.

**Notes:** The DB's current Article 85 content (AI Office establishment) duplicates the substance of real Article 64, which is itself separately corrected above. Real Article 85 is the data-subject/affected-person complaint right, a genuinely new, previously-missing data point (the audit flags this as a real product gap: "whether company has a process for handling AI-related complaints from affected persons"). No existing field captures this; it is a Tier B Evidence Center candidate per the audit's data-gap recommendations, not something to wire up as part of this content-only correction.

---

## Article 88

**Current (wrong) title:** AI systems and GPAI models for general security purposes
**Current (wrong) description (truncated to ~2 sentences):** AI systems and GPAI models specifically developed and used for national security, military, or defence purposes are excluded from this Regulation. This exclusion is interpreted strictly. Dual-use AI (civilian and military) is only excluded for the...

**Corrected title:** Enforcement of the obligations of providers of general-purpose AI models
**Corrected description (full, from the real Regulation text):** The Commission has exclusive power to supervise and enforce Chapter V (general-purpose AI model obligations), subject to the Article 94 procedural guarantees, and shall entrust implementation to the AI Office without prejudice to the Commission's own powers of organisation and the division of competences between Member States and the Union. Market surveillance authorities may, without prejudice to Article 75(3), request the Commission to exercise these powers where necessary and proportionate to support their own tasks.
**Corrected plain_english:** Only the European Commission, acting through the AI Office, enforces the rules for general-purpose AI model providers; national regulators can ask the Commission to step in but cannot enforce Chapter V themselves.

**Notes:** Military/defence/national-security exclusion is genuinely in the Regulation, but at Article 2(3) (scope), not Article 88, as the audit doc itself notes. The DB's current Article 88 content is a real but misplaced legal point. No legitimate profile_field for the corrected content.

---

## Article 89

**Current (wrong) title:** AI systems with specific transparency obligations
**Current (wrong) description (truncated to ~2 sentences):** The Commission and Member States shall facilitate the development of voluntary codes of conduct for AI systems that are not high-risk under this Regulation, but may present specific transparency or other risks. Codes of conduct may also cover environmental...

**Corrected title:** Monitoring actions
**Corrected description (full, from the real Regulation text):** The AI Office may take necessary actions to monitor effective implementation of and compliance with this Regulation by general-purpose AI model providers, including adherence to approved codes of practice. Downstream providers have the right to lodge a duly reasoned complaint alleging an infringement, identifying the GPAI provider's point of contact, the relevant facts and provisions concerned, why they believe an infringement occurred, and any other relevant information.
**Corrected plain_english:** The AI Office actively monitors whether general-purpose AI model providers are following the rules, and businesses building on top of someone else's AI model can formally complain if they believe that model's provider is breaking the law.

**Notes:** Transparency obligations for chatbots, synthetic content, etc. are already correctly covered at real Article 50, confirmed MATCH in the DB. The DB's current Article 89 content duplicates that topic under the wrong number. No legitimate profile_field for the corrected content.

---

## Article 90

**Current (wrong) title:** European Artificial Intelligence Board
**Current (wrong) description (truncated to ~2 sentences):** A European Artificial Intelligence Board (AI Board) is established, composed of representatives of national market surveillance authorities and the European Data Protection Supervisor. The AI Board shall provide advice and assistance to the Commission...

**Corrected title:** Alerts of systemic risks by the scientific panel
**Corrected description (full, from the real Regulation text):** The scientific panel may issue a qualified alert to the AI Office where it has reason to suspect a general-purpose AI model poses a concrete identifiable risk at Union level, or meets the systemic-risk conditions of Article 51. On a qualified alert, the Commission, through the AI Office and after informing the Board, may exercise its powers to assess the matter, and the AI Office shall inform the Board of any subsequent measures under Articles 91-94. A qualified alert must be duly reasoned, identifying the relevant provider's contact point, a description of the facts and reasons for the alert, and any other relevant information.
**Corrected plain_english:** Independent AI experts can formally flag a general-purpose AI model to the EU's AI Office if they believe it poses a real risk, triggering a Commission-led investigation.

**Notes:** The Board's establishment is correctly covered at real Article 65, which is itself separately corrected above (currently mislabeled "Article 90's neighbor" in the cascade). The DB's current Article 90 content duplicates the Board-establishment topic under the wrong number. No legitimate profile_field for the corrected content.

---

## Article 91

**Current (wrong) title:** Tasks of the AI Board
**Current (wrong) description (truncated to ~2 sentences):** The AI Board's tasks include: providing opinions on standardisation, conformity assessment, classification of AI systems; supporting the Commission; fostering cooperation between national authorities; contributing to uniform application; providing guidance...

**Corrected title:** Power to request documentation and information
**Corrected description (full, from the real Regulation text):** The Commission may request a general-purpose AI model provider to supply the technical documentation prepared under Articles 53 and 55, or any additional necessary information to assess compliance. The AI Office may first initiate a structured dialogue. Upon a substantiated request from the scientific panel, the Commission may also request information necessary for the panel's tasks. The request must state its legal basis and purpose, specify what is required, set a deadline, and indicate the Article 101 fines for incorrect, incomplete or misleading information. The provider (or its authorised legal representative) must supply the requested information; lawyers may supply it on the client's behalf, but the client remains fully responsible if it is incomplete, incorrect or misleading.
**Corrected plain_english:** The European Commission can formally demand documentation or information from a general-purpose AI model provider to check compliance, and giving false or incomplete answers can trigger fines.

**Notes:** The Board's tasks are correctly covered at real Article 66, which is itself separately corrected above. The DB's current Article 91 content duplicates that topic under the wrong number; this means the DB currently has "Board tasks" content appearing twice (mislabeled at both 66's neighbor position and 91), while the genuine Article 91 power (documentation requests to GPAI providers) is entirely absent. This row does have a real customer-actionable data point: "whether company can respond to AI Office documentation requests for its GPAI model," currently NO existing field, per the audit. No existing field maps to it; this is a genuine, separate product gap, not something to fix by simple field renaming.

---

## Article 92

**Current (wrong) title:** Scientific panel of independent experts
**Current (wrong) description (truncated to ~2 sentences):** The Commission shall establish a scientific panel of independent AI experts to provide technical advice and support to the AI Office and the Board. The panel shall assist in evaluating GPAI models for systemic risk, advise on technical standards, and...

**Corrected title:** Power to conduct evaluations
**Corrected description (full, from the real Regulation text):** The AI Office, after consulting the Board, may evaluate a general-purpose AI model to assess provider compliance (where Article 91 information is insufficient) or to investigate systemic risks, particularly following a qualified alert. The Commission may appoint independent experts, including from the scientific panel, to carry out evaluations, meeting the Article 68(2) criteria. The Commission may request access to the model through APIs or other technical means, including source code, stating the legal basis, purpose, deadline, and the Article 101 fines for failure to provide access. The Commission shall set out detailed evaluation arrangements by implementing act, and the AI Office may initiate a structured dialogue with the provider before requesting access.
**Corrected plain_english:** The AI Office can run its own technical evaluation of a general-purpose AI model, including getting direct access to its source code or APIs, if it suspects the model is non-compliant or poses systemic risk.

**Notes:** The scientific panel's establishment is correctly covered at real Article 68, which is itself separately corrected above. The DB's current Article 92 content duplicates that topic under the wrong number. No legitimate profile_field for the corrected content (this is a regulator-facing investigatory power, not a customer obligation).

---

## Article 93

**Current (wrong) title:** Advisory forum
**Current (wrong) description (truncated to ~2 sentences):** An advisory forum shall be established to provide stakeholder advice to the AI Board and the Commission. The forum shall represent a balanced mix of stakeholders including industry, start-ups, SMEs, civil society, academia, and fundamental rights...

**Corrected title:** Power to request measures
**Corrected description (full, from the real Regulation text):** Where necessary and appropriate, the Commission may request providers of general-purpose AI models to take measures complying with Articles 53 and 54, implement mitigation measures where an Article 92 evaluation raises serious and substantiated systemic-risk concerns, or restrict, withdraw or recall the model. Before requesting a measure, the AI Office may initiate a structured dialogue. If, during that dialogue, the provider offers binding commitments to mitigate a systemic risk, the Commission may, by decision, make those commitments binding and declare the matter closed.
**Corrected plain_english:** If the AI Office's evaluation finds serious systemic-risk problems with your general-purpose AI model, the Commission can formally order you to fix it, mitigate the risk, or pull the model from the market.

**Notes:** The advisory forum's establishment is correctly covered at real Article 67, which is itself separately corrected above. The DB's current Article 93 content duplicates that topic under the wrong number. No legitimate profile_field for the corrected content (regulator-facing enforcement power, not a customer obligation).

---

## Article 94

**Current (wrong) title:** Involvement of the Advisory Forum in the functioning of the Board
**Current (wrong) description (truncated to ~2 sentences):** The Advisory Forum shall be invited to participate in the work of the Board and to attend its meetings where relevant topics are discussed. The Board shall consider advisory forum opinions when developing guidelines and recommendations. The forum shall...

**Corrected title:** Procedural rights of economic operators of the general-purpose AI model
**Corrected description (full, from the real Regulation text):** Article 18 of Regulation (EU) 2019/1020 (rights of economic operators, including the right to be heard) applies, with the necessary modifications, to providers of general-purpose AI models, without prejudice to any more specific procedural rights provided elsewhere in this Regulation.
**Corrected plain_english:** If the AI Office takes enforcement action against your general-purpose AI model, you keep the same due-process rights as any other economic operator under EU market surveillance law, including the right to be heard.

**Notes:** This is a real, separate due-process right that the audit flagged as a genuine, currently-uncaptured data point: "whether company (as a GPAI provider) has been given due-process rights before AI Office sanctions." There is no "Involvement of the Advisory Forum" content as a standalone article at this number in the real text; that topic does not require its own article since advisory forum participation in Board meetings is already covered within real Article 67 (corrected above). No legitimate profile_field for the corrected content; this is fundamentally a description of a procedural right, not a compliance obligation requiring a customer flag.

---

## Article 99

**Current (wrong) title:** Amendments to Regulation (EU) No 300/2008
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) No 300/2008 on civil aviation security is amended to ensure AI systems used in aviation security contexts comply with the AI Act requirements.

**Corrected title:** Penalties
**Corrected description (full, from the real Regulation text):** Member States shall lay down rules on penalties and enforcement measures (which may include warnings and non-monetary measures), effective, proportionate and dissuasive, taking into account SME interests and economic viability, and shall notify the Commission of these rules and any subsequent amendments. Non-compliance with the Article 5 prohibited practices is subject to administrative fines of up to EUR 35,000,000 or, for undertakings, up to 7% of total worldwide annual turnover for the preceding financial year, whichever is higher. Non-compliance with other operator or notified-body obligations (provider obligations under Article 16, authorised representative obligations under Article 22, importer obligations under Article 23, distributor obligations under Article 24, deployer obligations under Article 26, notified body requirements under Articles 31/33/34, or transparency obligations under Article 50) is subject to fines of up to EUR 15,000,000 or 3% of worldwide turnover, whichever is higher. Supplying incorrect, incomplete or misleading information to notified bodies or national authorities is subject to fines of up to EUR 7,500,000 or 1% of worldwide turnover, whichever is higher. For SMEs, the lower of the percentage or fixed amount applies. The Article sets out detailed factors authorities must weigh when setting fine amounts (nature, gravity, duration, prior fines, cooperation, intent, mitigation, etc.), rules for fines on public authorities, judicial procedural safeguards, and an annual Member State reporting duty to the Commission.
**Corrected plain_english:** This is the EU AI Act's core fines article. Banned AI practices can cost up to 35 million euros or 7% of global revenue, whichever is higher. Breaking most other rules, like high-risk system obligations or transparency duties, can cost up to 15 million euros or 3% of global revenue. Giving regulators false or misleading information can cost up to 7.5 million euros or 1% of global revenue. Small businesses get reduced caps.

**Notes:** This is the single most severe and highest-priority correction in the entire audit. The DB currently labels Article 99 as an unrelated aviation-security legislative amendment; the real Article 99 is the penalties article that sets the EUR 35M/7% fine for Article 5 violations and the EUR 15M/3% fine for most other violations. This content currently sits, misplaced, under the DB's Article 79 (see that entry above, where it has been removed and replaced with Article 79's correct content). No `profile_field` exists or is needed; this article is informational/risk-exposure context, used by the remediation engine to communicate fine exposure for gaps found elsewhere, not a standalone applicability check.

---

## Article 100

**Current (wrong) title:** Amendments to Regulation (EU) No 167/2013
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) No 167/2013 on agricultural and forestry vehicle approval is amended to ensure AI systems used in agricultural/forestry vehicles comply with the AI Act.

**Corrected title:** Administrative fines on Union institutions, bodies, offices and agencies
**Corrected description (full, from the real Regulation text):** The European Data Protection Supervisor may impose administrative fines on EU institutions, bodies, offices and agencies within scope of this Regulation, weighing the same kind of factors as Article 99 (nature, gravity, duration, responsibility, cooperation, mitigation, prior infringements, how the infringement came to light, and the institution's annual budget). Non-compliance with the Article 5 prohibited practices is subject to fines of up to EUR 1,500,000; non-compliance with other requirements is subject to fines of up to EUR 750,000. The Supervisor must give the institution a hearing opportunity, base decisions only on matters parties could comment on, respect rights of defence and file access (subject to confidentiality), and report fines to the Commission annually. Fines collected go to the EU general budget and must not affect the institution's effective operation.
**Corrected plain_english:** EU institutions themselves (not private companies) face their own, separate, smaller fine scale for AI Act violations, enforced by the European Data Protection Supervisor rather than national regulators.

**Notes:** Not customer-actionable for ComplianceKit's typical private-sector tenants (this article applies specifically to EU institutions, bodies, offices and agencies). No legitimate profile_field. This is part of the consistent +3 numbering offset that runs from Article 99 through Article 112 minus one (real article N appears in the DB three numbers earlier, i.e. DB N = real N+3), as identified in the audit.

---

## Article 101

**Current (wrong) title:** Amendments to Regulation (EU) No 168/2013
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) No 168/2013 on the approval and market surveillance of two- or three-wheel vehicles and quadricycles is amended to cover AI systems in those vehicles.

**Corrected title:** Fines for providers of general-purpose AI models
**Corrected description (full, from the real Regulation text):** The Commission may impose fines on general-purpose AI model providers of up to 3% of worldwide annual turnover or EUR 15,000,000, whichever is higher, where it finds the provider intentionally or negligently infringed the Regulation, failed to comply with an Article 91 documentation/information request (or supplied false information), failed to comply with an Article 93 measure, or failed to provide model access for an Article 92 evaluation. Fine amounts consider the nature, gravity and duration of the infringement, proportionality, and any Article 93(3) commitments or code-of-practice adherence. The Commission must give the provider a hearing before deciding. Fines must be effective, proportionate and dissuasive; the Court of Justice of the EU has unlimited jurisdiction to review, cancel, reduce or increase them.
**Corrected plain_english:** General-purpose AI model providers face their own dedicated fine, up to 15 million euros or 3% of global revenue, for breaking GPAI-specific rules like ignoring documentation requests or refusing model access for an official evaluation.

**Notes:** This content currently sits, misplaced, under the DB's Article 80 (see that entry above, where it has been removed and replaced with Article 80's correct content). The EUR 15M/3% figure that was misplaced at DB Article 80 is the correct figure here. No legitimate profile_field exists for a direct applicability check, but this is informational fine-exposure context relevant to any tenant with `ai_act_data.uses_gpai == true`.

---

## Article 102

**Current (wrong) title:** Amendments to Directive 2014/90/EU
**Current (wrong) description (truncated to ~2 sentences):** Directive 2014/90/EU on marine equipment is amended to ensure marine AI systems comply with the EU AI Act requirements.

**Corrected title:** Amendment to Regulation (EC) No 300/2008
**Corrected description (full, from the real Regulation text):** Article 4(3) of Regulation (EC) No 300/2008 (civil aviation security) is amended to add a subparagraph requiring that, when adopting technical specifications and approval/use procedures for AI-based security equipment within the meaning of this Regulation, the Chapter III Section 2 high-risk AI requirements be taken into account.
**Corrected plain_english:** A separate EU aviation security law is updated so that any AI used in airport security screening equipment also has to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. Subject matter (aviation security) is the same topic the DB currently misattributes to its own Article 99, just at the correct real article number and with the correct legal mechanism (a cross-reference amendment, not a freestanding obligation). No legitimate profile_field; relevant only to aviation security equipment operators.

---

## Article 103

**Current (wrong) title:** Amendments to Directive (EU) 2016/797
**Current (wrong) description (truncated to ~2 sentences):** Directive (EU) 2016/797 on the interoperability of the rail system is amended to ensure AI systems used in rail interoperability comply with the EU AI Act.

**Corrected title:** Amendment to Regulation (EU) No 167/2013
**Corrected description (full, from the real Regulation text):** Article 17(5) of Regulation (EU) No 167/2013 (agricultural and forestry vehicle approval) is amended to add a subparagraph requiring that delegated acts concerning AI systems which are safety components within the meaning of this Regulation take into account the Chapter III Section 2 high-risk requirements.
**Corrected plain_english:** A separate EU law on agricultural and forestry vehicle approval is updated so AI safety components in those vehicles also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. No legitimate profile_field; relevant only to agricultural/forestry vehicle AI component manufacturers.

---

## Article 104

**Current (wrong) title:** Amendments to Regulation (EU) 2018/858
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) 2018/858 on the approval and market surveillance of motor vehicles is amended to ensure AI systems in motor vehicles comply with the EU AI Act.

**Corrected title:** Amendment to Regulation (EU) No 168/2013
**Corrected description (full, from the real Regulation text):** Article 22(5) of Regulation (EU) No 168/2013 (two/three-wheel vehicles and quadricycles) is amended to add a subparagraph requiring delegated acts concerning AI safety components to take into account the Chapter III Section 2 high-risk requirements.
**Corrected plain_english:** A separate EU law on motorbikes, mopeds, and quadricycles is updated so AI safety components in those vehicles also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. No legitimate profile_field; relevant only to two/three-wheel vehicle and quadricycle manufacturers.

---

## Article 105

**Current (wrong) title:** Amendments to Regulation (EU) 2019/2144
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) 2019/2144 on type-approval requirements for motor vehicles with regard to their general safety is amended to ensure autonomous and AI-equipped vehicles comply with the EU AI Act.

**Corrected title:** Amendment to Directive 2014/90/EU
**Corrected description (full, from the real Regulation text):** Article 8 of Directive 2014/90/EU (marine equipment) is amended to add a paragraph requiring that, when carrying out its activities and adopting technical specifications and testing standards, the Commission take into account the Chapter III Section 2 high-risk requirements for AI systems that are safety components.
**Corrected plain_english:** A separate EU law on marine equipment is updated so AI safety components used on ships also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. No legitimate profile_field; relevant only to marine equipment manufacturers.

---

## Article 106

**Current (wrong) title:** Amendments to Regulation (EU) 2020/1056
**Current (wrong) description (truncated to ~2 sentences):** Regulation (EU) 2020/1056 on electronic freight transport information is amended to ensure AI systems used in electronic freight transport information comply with the EU AI Act.

**Corrected title:** Amendment to Directive (EU) 2016/797
**Corrected description (full, from the real Regulation text):** Article 5 of Directive (EU) 2016/797 (rail system interoperability) is amended to add a paragraph requiring that, when adopting delegated and implementing acts concerning AI systems which are safety components, the Chapter III Section 2 high-risk requirements be taken into account.
**Corrected plain_english:** A separate EU law on railway interoperability is updated so AI safety components used in trains also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. The DB's current Article 106 reference to "Regulation (EU) 2020/1056" is confirmed, on direct PDF review, not to appear anywhere among the twelve legal instruments the real Regulation actually amends (Regulation EC 300/2008, Regulations EU 167/2013, 168/2013, 2018/858, 2018/1139, 2019/2144, and Directives 2014/90/EU, 2016/797, 2020/1828, as listed in the Article 113 recital and the Regulation's own amending list). This appears to be a fabricated reference, not just a numbering drift. No legitimate profile_field; relevant only to rail equipment manufacturers.

---

## Article 107

**Current (wrong) title:** Amendments to Regulation (EU) No 575/2013
**Current (wrong) description (truncated to ~2 sentences):** The Capital Requirements Regulation (EU) No 575/2013 is amended to ensure AI systems used by credit institutions in credit risk assessment and other financial services comply with the EU AI Act requirements alongside existing financial sector regulation...

**Corrected title:** Amendment to Regulation (EU) 2018/858
**Corrected description (full, from the real Regulation text):** Article 5 of Regulation (EU) 2018/858 (motor vehicle approval and market surveillance) is amended to add a paragraph requiring that delegated acts concerning AI safety components take into account the Chapter III Section 2 high-risk requirements.
**Corrected plain_english:** A separate EU law on motor vehicle approval is updated so AI safety components used in cars and trucks also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. The DB's current Article 107 reference to "Regulation (EU) No 575/2013" (the Capital Requirements Regulation) is confirmed, on direct PDF review, not to appear among the actual twelve amended instruments. This is a fabricated reference, not just numbering drift, same issue as Article 106. No legitimate profile_field; relevant only to motor vehicle manufacturers.

---

## Article 108

**Current (wrong) title:** Amendments to Directive 2013/36/EU
**Current (wrong) description (truncated to ~2 sentences):** The Capital Requirements Directive (CRD IV) is amended to align AI governance requirements in banking with the EU AI Act. Banks must ensure their AI risk management frameworks are consistent with both prudential requirements and AI Act obligations.

**Corrected title:** Amendments to Regulation (EU) 2018/1139
**Corrected description (full, from the real Regulation text):** Regulation (EU) 2018/1139 (EU aviation safety rules) is amended in six places (Articles 17, 19, 43, 47, 57, 58) to add provisions requiring that, when adopting delegated or implementing acts concerning AI systems which are safety components within the meaning of this Regulation, the Chapter III Section 2 high-risk requirements be taken into account.
**Corrected plain_english:** A separate EU aviation safety law is updated in six different places so AI safety components used in aircraft systems also have to meet the AI Act's high-risk AI rules.

**Notes:** +3 offset continues. The DB's current Article 108 reference to "Directive 2013/36/EU" (the Capital Requirements Directive, CRD IV) is confirmed, on direct PDF review, not to appear among the actual amended instruments. This is a fabricated reference, same issue as Articles 106 and 107. No legitimate profile_field; relevant only to aviation safety equipment manufacturers.

---

## Article 109

**Current (wrong) title:** AI systems already placed on the market or put into service
**Current (wrong) description (truncated to ~2 sentences):** AI systems that have already been placed on the market or put into service before this Regulation applies shall be brought into compliance with this Regulation by 2 August 2027 unless they are subject to a substantial modification. For GPAI models placed on the market before August 2025, providers shall take necessary steps to comply with GPAI obligations by 2 August 2025.

**Corrected title:** Amendment to Regulation (EU) 2019/2144
**Corrected description (full, from the real Regulation text):** Article 11 of Regulation (EU) 2019/2144 (general motor vehicle safety type-approval) is amended to add a paragraph requiring that implementing acts concerning AI safety components take into account the Chapter III Section 2 high-risk requirements.
**Corrected plain_english:** A separate EU law on motor vehicle safety type-approval is updated so AI safety components used in vehicle safety systems also have to meet the AI Act's high-risk AI rules.

**Notes:** This is the article where the DB's current title and topic accidentally land on a real legal concept (transitional/grandfathering provisions for legacy AI systems) that genuinely exists in the Regulation, just three articles later, at real Article 111 (see that entry below, where this content has been moved). The +3 offset continues here too. No legitimate profile_field for the corrected (amendment) content at Article 109 itself.

---

## Article 110

**Current (wrong) title:** Evaluation and review
**Current (wrong) description (truncated to ~2 sentences):** By 2 August 2029 and every 4 years thereafter, the Commission shall assess and report to the European Parliament and Council on the implementation and impact of this Regulation. The review shall cover: effectiveness of the prohibited practices list...

**Corrected title:** Amendment to Directive (EU) 2020/1828
**Corrected description (full, from the real Regulation text):** Annex I to Directive (EU) 2020/1828 (representative actions for consumer collective interests) is amended to add this Regulation to the list of laws that can be the subject of a representative action, by inserting a reference to Regulation (EU) 2024/1689 as point (68) of that Annex.
**Corrected plain_english:** A separate EU consumer protection law is updated so that consumer groups can bring collective legal action (like a class action) over AI Act violations, the same way they already can for other consumer-protection laws.

**Notes:** The DB's "Evaluation and review" topic genuinely exists in the real Regulation, just three articles later at real Article 112 (see that entry below, where this content has been moved). The +3 offset continues here too. No legitimate profile_field for the corrected (amendment) content at Article 110 itself, but this is a significant practical point that ComplianceKit customers should be aware their AI Act violations could trigger EU-style class actions, not just regulator fines.

---

## Article 111

**Current (wrong) title:** Repeal
**Current (wrong) description (truncated to ~2 sentences):** There are no prior EU-wide AI regulations to repeal. This Regulation establishes the first comprehensive EU AI regulatory framework. Member State national AI laws that conflict with this Regulation shall be superseded by this Regulation where it applies.

**Corrected title:** AI systems already placed on the market or put into service and general-purpose AI models already placed on the market
**Corrected description (full, from the real Regulation text):** Without prejudice to Article 5 applying per Article 113(3)(a), AI systems that are components of large-scale IT systems established by the Annex X legal acts and that were placed on the market or put into service before 2 August 2027 must be brought into compliance by 31 December 2030. This Regulation's requirements must be considered in the evaluation of each such large-scale IT system whenever those legal acts are replaced or amended. Separately, for other high-risk AI systems placed on the market or put into service before 2 August 2026, this Regulation applies only if those systems undergo significant design changes from that date onward, except that providers and deployers of high-risk AI systems intended for use by public authorities must comply by 2 August 2030 regardless. Providers of general-purpose AI models placed on the market before 2 August 2025 must take the necessary steps to comply with this Regulation's obligations by 2 August 2027.
**Corrected plain_english:** AI systems and general-purpose AI models that were already on the market before the AI Act's deadlines get extra time to comply, generally until 2027 or, for large IT systems and public-sector high-risk systems, as late as 2030, unless they are significantly redesigned sooner.

**Notes:** There is no standalone "Repeal" article anywhere in the real Regulation text reviewed; the AI Act does not repeal a predecessor act, it is a new regulation, so the DB's current Article 111 content is fabricated. The genuine "legacy systems compliance deadline" content the DB currently has mislabeled as Article 109 belongs here instead, restoring the original transitional-provisions topic to its correct number (this is the final article in the +3 offset zone; Article 112 below also shifts, but Article 113, "Entry into force and application," correctly realigns at both ends per the audit). This is the article that should carry the `ai_act_data.uses_ai` profile_field check the DB currently has on its mislabeled Article 109 row, since it captures genuinely actionable compliance-deadline information.

---

## Article 112

**Current (wrong) title:** Transitional provisions
**Current (wrong) description (truncated to ~2 sentences):** Application timeline: prohibited AI practices (Article 5) apply from 2 February 2025; GPAI model obligations (Chapter V) and governance provisions apply from 2 August 2025; high-risk AI obligations in Annex I products (Chapter III) apply from 2 August...

**Corrected title:** Evaluation and review
**Corrected description (full, from the real Regulation text):** The Commission shall annually assess the need to amend the Annex III high-risk list and the Article 5 prohibited-practices list, reporting findings to Parliament and Council. By 2 August 2028 and every four years thereafter, it shall evaluate and report on Annex III amendments, Article 50 transparency-measure amendments, and supervision/governance effectiveness improvements. By 2 August 2029 and every four years thereafter, it shall report on the Regulation's overall evaluation and review, including whether enforcement structure needs a dedicated EU agency, accompanied by amendment proposals where appropriate. Reports must address national competent authorities' resourcing, the state of administrative fines applied by Member States, adopted harmonised standards, and SME market entry. By 2 August 2028, the Commission shall separately evaluate whether the AI Office needs more powers or resources. It shall also report periodically on energy-efficiency standardisation progress for general-purpose AI models and on the impact of voluntary codes of conduct. By 2 August 2031, the Commission shall conduct a dedicated enforcement assessment.
**Corrected plain_english:** The European Commission is required to keep reviewing and reporting on how well the AI Act is working, roughly every year for the high-risk and prohibited-practices lists and every four years for the bigger structural questions, including whether a dedicated EU AI enforcement agency is needed.

**Notes:** The DB's "Transitional provisions" topic the audit flagged here genuinely exists in the Regulation, but the actual application-timeline information (prohibited practices from 2 February 2025, GPAI from 2 August 2025, high-risk obligations from 2 August 2026) is set out across multiple provisions rather than as a single standalone "Transitional provisions" article at this number; the closest genuine transitional-deadline content is now correctly placed at real Article 111 above. This is the final article affected by the +3 offset; real Article 113 ("Entry into force and application") correctly realigns immediately after this and needs no correction, consistent with the audit's finding that Article 113 is MATCH.

---

## Summary of cross-references between corrected entries

- Article 79's misplaced penalties content moves to Article 99.
- Article 80's misplaced GPAI-fines content moves to Article 101.
- Article 109's misplaced legacy-systems-deadline content moves to Article 111.
- Article 110's misplaced evaluation-and-review content moves to Article 112.
- Article 52's misplaced GPAI-obligations content moves to Article 53; Article 53's misplaced systemic-risk-obligations content moves to Article 55; Article 54 must be newly inserted (real "Authorised representatives of providers of general-purpose AI models"); Article 55's invented "innovation support" content should be discarded; Article 56's misplaced Annex XIII content is replaced with the real "Codes of practice" article text.
- Article 32's content moves to Article 33; Article 33's to Article 34; Article 34's to Article 35; Article 35's to Article 36; Article 36's to Article 37; Article 37's to Article 38; Article 38's invented "Cybersecurity Act" content should be discarded in favour of the real "Coordination of notified bodies" text.
- Article 61's content moves to Article 62; Article 62's invented "report concerns" content should be discarded.
- Article 65's, 66's, 67's, 68's content (Board establishment, Board tasks, Advisory forum, Scientific panel) are each duplicated incorrectly at Articles 90, 91 (partially), 92, 93 respectively; corrected versions are provided at both the original (64-70 block) and duplicate (88-94 block) locations above, since both need fixing independently.
