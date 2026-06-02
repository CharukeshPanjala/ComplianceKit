"""
Seed script — NIS2 Directive (EU) 2022/2555 (46 articles)
Run locally:
  cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit \
    uv run python scripts/seeders/seed_nis2.py
"""
import asyncio
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from common.config import BaseServiceSettings
from common.models.regulation import Regulation, RegulationVersion, RegulationStatus, DetectedBy
from common.models.rule import Rule, Severity

settings = BaseServiceSettings()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ── Regulation ────────────────────────────────────────────────────────────────

NIS2_REGULATION = {
    "name": "NIS2",
    "full_name": "Network and Information Security Directive 2 (EU) 2022/2555",
    "jurisdiction": "EU",
    "authority": "European Union Agency for Cybersecurity (ENISA)",
    "current_version": "2022/2555",
    "effective_date": date(2023, 1, 16),
    "status": RegulationStatus.ACTIVE,
    "description": (
        "Directive (EU) 2022/2555 on measures for a high common level of cybersecurity across "
        "the Union. NIS2 replaces NIS1 (2016/1148) and significantly expands scope to cover "
        "essential and important entities across 18 sectors. Member States must transpose NIS2 "
        "into national law. Deadline for transposition was 17 October 2024."
    ),
    "source_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022L2555",
}

NIS2_VERSION = {
    "version_number": "2022.1",
    "version_label": "NIS2 Directive 2022/2555 (Original)",
    "effective_date": date(2023, 1, 16),
    "detected_by": DetectedBy.MANUAL,
}

# ── Articles ──────────────────────────────────────────────────────────────────

NIS2_ARTICLES = [

    # Chapter I — General Provisions
    {
        "article": "Article 1", "article_number": 1,
        "title": "Subject matter",
        "chapter": "Chapter I — General Provisions", "category": "General",
        "description": "This Directive lays down measures aimed at achieving a high common level of cybersecurity across the Union, with a view to improving the functioning of the internal market. It establishes obligations for Member States to adopt national cybersecurity strategies, designate competent authorities, establish CSIRTs, and adopt supervisory and enforcement measures.",
        "plain_english": "NIS2 sets the framework for cybersecurity across the EU — requiring governments to have strategies, authorities, and incident response teams, and requiring organisations to meet security standards.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "general", "scope"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Understand whether NIS2 applies to your organisation based on sector and size thresholds.",
    },
    {
        "article": "Article 2", "article_number": 2,
        "title": "Scope",
        "chapter": "Chapter I — General Provisions", "category": "General",
        "description": "This Directive applies to public or private entities of a type referred to in Annexes I and II that qualify as medium-sized enterprises under Article 2 of the Annex to Recommendation 2003/361/EC, or exceed the ceilings for medium-sized enterprises, and which provide their services or carry out their activities within the Union. Essential sectors (Annex I): energy, transport, banking, financial market infrastructure, health, drinking water, wastewater, digital infrastructure, ICT service management, public administration, space. Important sectors (Annex II): postal and courier services, waste management, manufacture/production and distribution of chemicals, food production, manufacturing, digital providers, research.",
        "plain_english": "NIS2 applies to medium and large organisations in 18 critical sectors. Small companies (under 50 employees, under €10M turnover) are generally exempt unless they are sole providers of critical services.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "profile_field",
        "profile_field": "nis2_data.nis2_sectors",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "scope", "essential_entities", "important_entities", "sectors"],
        "evaluation_logic": {"type": "profile_field", "check": "nis2_data.nis2_sectors is not empty AND meets size threshold"},
        "remediation_hint": "Assess whether your organisation falls within NIS2 scope based on sector (Annex I/II) and size. Register with your national competent authority if in scope.",
    },
    {
        "article": "Article 3", "article_number": 3,
        "title": "Essential and important entities",
        "chapter": "Chapter I — General Provisions", "category": "General",
        "description": "Entities shall be considered essential entities if they: are large enterprises in Annex I sectors; are certain categories of public administration; are qualified trust service providers, TLD name registries, DNS service providers, or certain domain name registration entities; are sole providers of a service essential for society/economy; or are identified by Member States due to their critical nature. All other entities in Annex I and II that do not qualify as essential are important entities. Essential entities face stricter supervision than important entities.",
        "plain_english": "Essential entities (stricter rules, proactive supervision) vs important entities (lighter touch, reactive supervision) — your classification determines your compliance obligations and fine exposure.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "profile_field",
        "profile_field": "nis2_data.entity_type",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "essential_entity", "important_entity", "classification"],
        "evaluation_logic": {"type": "profile_field", "check": "nis2_data.entity_type is defined"},
        "remediation_hint": "Determine whether your organisation qualifies as essential or important. Essential entities face proactive supervision; important entities face reactive supervision.",
    },
    {
        "article": "Article 4", "article_number": 4,
        "title": "Sector-specific Union legal acts",
        "chapter": "Chapter I — General Provisions", "category": "General",
        "description": "Where sector-specific Union legal acts require essential or important entities to adopt cybersecurity risk-management measures or to notify significant incidents, and where those requirements are at least equivalent in effect to the obligations laid down in this Directive, the relevant provisions of this Directive shall not apply to those entities. NIS2 acts as a cybersecurity baseline; sector-specific rules (e.g. DORA for financial sector) may take precedence where they are equivalent or stricter.",
        "plain_english": "If your sector has its own EU cybersecurity law (e.g. DORA for finance, NIS2 for energy), those sector-specific rules apply instead of NIS2 where equivalent.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "industry", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "sector_specific", "DORA", "lex_specialis"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Check whether your sector has specific EU cybersecurity legislation (e.g. DORA for financial entities) that may supplement or replace some NIS2 obligations.",
    },

    # Chapter II — Coordinated Cybersecurity Frameworks
    {
        "article": "Article 5", "article_number": 5,
        "title": "National cybersecurity strategy",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "National Framework",
        "description": "Each Member State shall adopt a national cybersecurity strategy covering: objectives and priorities; governance framework; measures on preparedness, response, and recovery; education, awareness, and training; research and development priorities; measures to address supply chain cybersecurity risks; measures to promote and develop national cybersecurity industry; and international cooperation. Strategies shall be reviewed at least every five years.",
        "plain_english": "Every EU country must have a national cybersecurity strategy covering prevention, response, and education — reviewed every 5 years.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "national_strategy", "government"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Review your national cybersecurity strategy to understand government priorities and align your own security programme.",
    },
    {
        "article": "Article 6", "article_number": 6,
        "title": "Coordinated vulnerability disclosure and a European vulnerability database",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "Vulnerability Management",
        "description": "Member States shall designate a CSIRT as coordinator for coordinated vulnerability disclosure. ENISA shall establish and maintain a European vulnerability database for publicly known vulnerabilities in ICT products and ICT services, accessible to the public. ENISA shall adopt adequate technical and organisational measures to ensure the security of the database.",
        "plain_english": "EU countries must have a coordinated vulnerability disclosure process, and ENISA maintains a European vulnerability database.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "vulnerability_disclosure", "ENISA"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Monitor ENISA's European vulnerability database and your national CSIRT's coordinated vulnerability disclosure programme.",
    },
    {
        "article": "Article 7", "article_number": 7,
        "title": "National cyber crisis management framework",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "National Framework",
        "description": "Each Member State shall designate one or more competent authorities responsible for cyber crisis management. Member States shall designate a national cyber crisis management authority and identify capabilities, assets, and procedures that can be deployed in cases of large-scale cybersecurity incidents and crises. Cooperation between civil and criminal authorities on cybersecurity shall be ensured.",
        "plain_english": "Each EU country must have a cyber crisis management framework with designated authorities for handling large-scale cybersecurity incidents.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "crisis_management", "government"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Know your national cyber crisis management authority and their escalation procedures for large-scale incidents.",
    },
    {
        "article": "Article 8", "article_number": 8,
        "title": "Competent authorities and single point of contact",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "National Framework",
        "description": "Each Member State shall designate one or more competent authorities responsible for cybersecurity and the supervisory tasks under this Directive. Member States shall designate a single point of contact to exercise a liaison function to ensure cross-border cooperation of Member State authorities. Member States may designate an existing authority as competent authority and single point of contact.",
        "plain_english": "Each EU country designates a national cybersecurity authority and a single point of contact for cross-border cooperation — this is who you report incidents to.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "competent_authority", "reporting"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Identify your national NIS2 competent authority — this is where you register and report incidents.",
    },
    {
        "article": "Article 9", "article_number": 9,
        "title": "CSIRTs",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "National Framework",
        "description": "Each Member State shall designate one or more CSIRTs (Computer Security Incident Response Teams). CSIRTs may be established within a competent authority. CSIRTs shall have adequate resources and technical capabilities. CSIRTs shall be available 24/7 and their contact information shall be made publicly available. CSIRTs shall monitor and analyse cybersecurity threats, vulnerabilities and incidents at national level.",
        "plain_english": "Every EU country must have 24/7 Computer Security Incident Response Teams (CSIRTs) that monitor threats and help entities respond to incidents.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "CSIRT", "incident_response"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Know your national CSIRT contact details. In a cyber incident, your CSIRT is a resource for technical assistance and threat intelligence.",
    },
    {
        "article": "Article 10", "article_number": 10,
        "title": "Requirements for CSIRTs",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "National Framework",
        "description": "CSIRTs shall meet the following requirements: have a high level of availability of communication channels; be located in a secure facility; be equipped with a backup system; have staff with relevant skills; be subject to IT security quality management; operate on a 24/7 basis; participate in EU-level cooperation networks. CSIRTs shall have well-defined processes for handling incidents and maintaining confidentiality of vulnerability information.",
        "plain_english": "National CSIRTs must meet specific technical and operational standards including 24/7 availability and secure infrastructure.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "CSIRT", "requirements"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — directly applies to government CSIRTs, not private organisations.",
    },
    {
        "article": "Article 11", "article_number": 11,
        "title": "Coordinated vulnerability disclosure",
        "chapter": "Chapter II — Coordinated Cybersecurity Frameworks", "category": "Vulnerability Management",
        "description": "Each Member State shall ensure there is a coordinated vulnerability disclosure policy. Member States shall take measures to facilitate the coordination between reporting entities, vendors and CSIRTs. CSIRTs act as trusted intermediaries facilitating the interaction between reporting persons and manufacturers or providers. Member States shall take necessary measures to allow security researchers to report vulnerabilities under legal protection.",
        "plain_english": "EU countries must have a coordinated vulnerability disclosure programme and protect security researchers who responsibly report vulnerabilities.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "policy_required",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "vulnerability_disclosure", "bug_bounty"],
        "evaluation_logic": {"type": "policy_required", "required_policies": ["vulnerability_disclosure_policy"]},
        "remediation_hint": "Implement a vulnerability disclosure policy (VDP) allowing security researchers to safely report vulnerabilities in your systems.",
    },

    # Chapter III — Cybersecurity Risk Management and Reporting
    {
        "article": "Article 12", "article_number": 12,
        "title": "Cyber crisis management",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Crisis Management",
        "description": "Member States shall establish an EU-CyCLONe network to support coordinated management of large-scale cybersecurity incidents and crises at operational level. EU-CyCLONe shall be composed of representatives of Member State cyber crisis management authorities and the Commission. EU-CyCLONe shall build capability and preparedness for large-scale cybersecurity incidents and crises that may have a significant cross-border impact.",
        "plain_english": "The EU has a network (EU-CyCLONe) to coordinate responses to large-scale cross-border cybersecurity incidents.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "EU_CyCLONe", "crisis_management"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — EU-CyCLONe is a government-level coordination body.",
    },
    {
        "article": "Article 13", "article_number": 13,
        "title": "Cooperation at Union level",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Cooperation",
        "description": "In order to pursue the objectives of this Directive and ensure its consistent implementation, Member States shall cooperate and, where appropriate, exchange information in the NIS Cooperation Group, CSIRTs network, and EU-CyCLONe. The NIS Cooperation Group shall facilitate strategic cooperation and exchange of information, and build trust among Member States.",
        "plain_english": "EU member states cooperate on cybersecurity through the NIS Cooperation Group, CSIRTs network, and EU-CyCLONe.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "cooperation", "NIS_Cooperation_Group"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — government-level cooperation framework.",
    },
    {
        "article": "Article 14", "article_number": 14,
        "title": "CSIRTs network",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Cooperation",
        "description": "A network of national CSIRTs is established. The CSIRTs network shall contribute to building confidence and trust between Member States and promote swift and effective operational cooperation. Tasks include exchanging information on incidents, threats and vulnerabilities; coordinating responses to cross-border incidents; and providing mutual assistance.",
        "plain_english": "EU national CSIRTs form a network to share threat intelligence and coordinate cross-border incident responses.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "CSIRT", "network", "cooperation"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — your national CSIRT participates in EU-wide threat intelligence sharing.",
    },
    {
        "article": "Article 15", "article_number": 15,
        "title": "NIS Cooperation Group",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Cooperation",
        "description": "A NIS Cooperation Group is established to support and facilitate strategic cooperation and the exchange of information among Member States and to develop trust and confidence. It shall be composed of representatives of Member States, the Commission and ENISA. Tasks include providing strategic guidance to the CSIRTs network, exchanging best practices on national cybersecurity strategies, and assisting Member States in building cybersecurity capabilities.",
        "plain_english": "The NIS Cooperation Group brings together EU governments and ENISA to share cybersecurity strategy and best practices.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "NIS_Cooperation_Group", "ENISA"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Follow NIS Cooperation Group publications for guidance on national and EU-level cybersecurity priorities.",
    },
    {
        "article": "Article 16", "article_number": 16,
        "title": "International cooperation",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Cooperation",
        "description": "The Union may conclude international agreements with third countries or international organisations allowing and organising their participation in certain activities of the NIS Cooperation Group and the CSIRTs network. Such agreements shall ensure adequate protection of personal data.",
        "plain_english": "The EU can form international cybersecurity cooperation agreements with non-EU countries.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "international_cooperation"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — relevant if operating in non-EU countries with international NIS2 cooperation agreements.",
    },
    {
        "article": "Article 17", "article_number": 17,
        "title": "Peer reviews",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Cooperation",
        "description": "The NIS Cooperation Group shall organise peer reviews with the aim of learning from shared experiences, strengthening mutual trust, achieving a high common level of cybersecurity and enhancing Member States' cybersecurity capabilities and policies. Peer reviews shall be carried out by cybersecurity experts designated by Member States.",
        "plain_english": "EU countries conduct mutual peer reviews of their cybersecurity capabilities to learn from each other.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "peer_review"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — government-level peer reviews.",
    },
    {
        "article": "Article 18", "article_number": 18,
        "title": "Reporting obligations — incidents",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Incident Reporting",
        "description": "Member States shall ensure that essential and important entities notify their CSIRT or competent authority of any incident having a significant impact on the provision of their services (significant incident). Notifications shall follow a three-step process: (1) early warning within 24 hours of becoming aware — indicating whether the incident is suspected to be the result of unlawful or malicious action; (2) incident notification within 72 hours — including initial assessment of severity and impact; (3) final report within one month — containing detailed description, type of threat, root cause, cross-border impact, and measures taken.",
        "plain_english": "Report significant cyber incidents in 3 steps: 24-hour early warning, 72-hour notification, and 1-month final report — to your national CSIRT or competent authority.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "profile_field",
        "profile_field": "nis2_data.has_incident_plan",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "incident_reporting", "24_hours", "72_hours", "significant_incident"],
        "evaluation_logic": {"type": "profile_field", "check": "nis2_data.has_incident_plan == true", "deadline_hours": 24},
        "remediation_hint": "Implement a 3-stage incident reporting workflow: 24h early warning, 72h notification, 1-month final report. Pre-register with your national competent authority.",
    },
    {
        "article": "Article 19", "article_number": 19,
        "title": "Use of European cybersecurity certification schemes",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Certification",
        "description": "Member States may require essential and important entities to use particular ICT products, ICT services and ICT processes certified under European cybersecurity certification schemes adopted pursuant to Article 49 of Regulation (EU) 2019/881 (the Cybersecurity Act). Member States shall not impose the use of a particular type of certified ICT product or service that does not have a corresponding European cybersecurity certification scheme.",
        "plain_english": "Countries can require use of EU-certified ICT products and services — based on ENISA's European cybersecurity certification framework.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "certification", "EU_Cybersecurity_Act"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Monitor national requirements for EU cybersecurity certified products in your sector. Check ENISA's certification schemes.",
    },
    {
        "article": "Article 20", "article_number": 20,
        "title": "Governance",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Governance",
        "description": "Member States shall ensure that the management bodies of essential and important entities approve the cybersecurity risk-management measures taken by those entities pursuant to Article 21, oversee its implementation, and can be held liable for infringements. Management bodies are required to follow cybersecurity training and to encourage entities to offer similar training to their employees on a regular basis to gain sufficient knowledge and skills to identify risks and assess cybersecurity risk-management practices and their impact on services.",
        "plain_english": "Your board/management body must approve and oversee cybersecurity measures, undergo cybersecurity training, and can be held personally liable for NIS2 violations.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "policy_required",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "governance", "management_liability", "board", "training"],
        "evaluation_logic": {"type": "policy_required", "required_policies": ["cybersecurity_governance_policy", "board_cybersecurity_training"]},
        "remediation_hint": "Ensure your board formally approves your cybersecurity risk management framework and undertakes regular cybersecurity training. Document their involvement.",
    },
    {
        "article": "Article 21", "article_number": 21,
        "title": "Cybersecurity risk-management measures",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Risk Management",
        "description": "Member States shall ensure that essential and important entities take appropriate and proportionate technical, operational and organisational measures to manage cybersecurity risks. Measures shall be based on an all-hazards approach and include at minimum: (a) risk analysis and information system security policies; (b) incident handling; (c) business continuity (backups, disaster recovery, crisis management); (d) supply chain security including third-party relationships; (e) security in network and information systems acquisition, development and maintenance including vulnerability handling and disclosure; (f) policies and procedures to assess the effectiveness of cybersecurity risk-management measures; (g) basic cyber hygiene practices and cybersecurity training; (h) policies and procedures regarding the use of cryptography and encryption; (i) human resources security, access control policies and asset management; (j) use of multi-factor authentication (MFA), continuous authentication solutions, secured voice/video/text communications, and secured emergency communications.",
        "plain_english": "The core NIS2 obligation — implement 10 minimum cybersecurity measures including risk management, incident response, BCP, supply chain security, encryption, MFA, and regular training.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "technical",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "risk_management", "security_measures", "MFA", "encryption", "BCP", "supply_chain"],
        "evaluation_logic": {
            "type": "technical",
            "required_measures": [
                "risk_analysis_policy",
                "incident_handling_procedure",
                "business_continuity_plan",
                "supply_chain_security_policy",
                "secure_development_policy",
                "security_effectiveness_assessment",
                "cyber_hygiene_training",
                "cryptography_policy",
                "access_control_policy",
                "mfa_implemented"
            ]
        },
        "remediation_hint": "Implement all 10 minimum NIS2 security measures. Use ISO 27001 or CIS Controls as a framework. Prioritise MFA, BCP, incident response, and supply chain security.",
    },
    {
        "article": "Article 22", "article_number": 22,
        "title": "Union level coordinated security risk assessments of critical supply chains",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Supply Chain",
        "description": "The NIS Cooperation Group, in cooperation with the Commission and ENISA, may carry out coordinated security risk assessments of specific critical ICT services, ICT systems or ICT products supply chains. These assessments shall take into account technical and non-technical risk factors, and shall identify mitigation measures. The results shall inform Member State policies and guidance for essential and important entities.",
        "plain_english": "The EU coordinates supply chain security risk assessments for critical ICT products and services — results feed into guidance for organisations.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "supply_chain", "risk_assessment"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Monitor EU coordinated supply chain risk assessment results — especially for 5G, cloud, and critical software supply chains.",
    },
    {
        "article": "Article 23", "article_number": 23,
        "title": "Reporting obligations",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Incident Reporting",
        "description": "Essential and important entities shall notify their CSIRT or competent authority of significant incidents without undue delay. A significant incident is one that has caused or is capable of causing severe operational disruption or financial loss to the entity concerned; or affected or is capable of affecting other natural or legal persons by causing considerable material or non-material damage. Notification timeline: without undue delay and in any event within 24 hours of becoming aware (early warning); within 72 hours of becoming aware (incident notification with initial assessment); upon request, an intermediate report; within one month of the incident notification (final report with full details). Entities shall also notify recipients of their services of significant incidents that are likely to adversely affect the provision of those services.",
        "plain_english": "Mandatory reporting timeline for significant incidents: 24h early warning → 72h notification → 1-month final report. Also notify affected customers.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "profile_field",
        "profile_field": "nis2_data.has_incident_plan",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "incident_reporting", "significant_incident", "24h", "72h", "notification"],
        "evaluation_logic": {"type": "profile_field", "check": "nis2_data.has_incident_plan == true", "deadline_hours": 24},
        "remediation_hint": "Build a 3-stage incident reporting process with pre-drafted notification templates. Test it in tabletop exercises. Know your national competent authority's reporting portal.",
    },
    {
        "article": "Article 24", "article_number": 24,
        "title": "Technical guidelines and methodological guidelines on incident reporting",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Incident Reporting",
        "description": "ENISA shall, in cooperation with the Commission, develop and maintain guidelines and a reporting template for significant incident notifications, to be adopted by implementing acts. The guidelines shall specify the format and content of notifications, thresholds for determining significance, and what constitutes a significant impact on service provision.",
        "plain_english": "ENISA provides standardised incident reporting templates and guidelines to help organisations report significant incidents correctly.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "incident_reporting", "ENISA", "guidelines"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Use ENISA's incident reporting guidelines and templates to ensure your notifications meet NIS2 requirements.",
    },
    {
        "article": "Article 25", "article_number": 25,
        "title": "Notification to recipients of services and to the public",
        "chapter": "Chapter III — Cybersecurity Risk Management and Reporting", "category": "Incident Reporting",
        "description": "Where a significant incident is likely to adversely affect the provision of services to recipients, essential and important entities shall notify those recipients without undue delay. Where public awareness is necessary to prevent or respond to a significant incident, or where disclosure is in the public interest, competent authorities or CSIRTs may inform the public or require the entity to do so.",
        "plain_english": "If a significant incident will affect your customers, notify them without delay. Authorities can also require public disclosure if it's in the public interest.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "policy_required",
        "profile_field": "nis2_data.has_incident_plan",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "customer_notification", "incident_disclosure"],
        "evaluation_logic": {"type": "policy_required", "required_policies": ["customer_incident_notification_procedure"]},
        "remediation_hint": "Include customer notification steps in your incident response plan with pre-approved communication templates.",
    },

    # Chapter IV — Jurisdiction and Registration
    {
        "article": "Article 26", "article_number": 26,
        "title": "Jurisdiction and territoriality",
        "chapter": "Chapter IV — Jurisdiction and Registration", "category": "Jurisdiction",
        "description": "Essential and important entities shall be deemed to fall under the jurisdiction of the Member State in which they are established. Entities providing DNS services, TLD name registries, cloud computing services, data centre services, CDN services, managed services, managed security services, online marketplace, online search engine, or social networking platform shall fall under the jurisdiction of the Member State in which they have their main establishment in the Union. DNS providers, TLD registries, and domain registration entities shall fall under the jurisdiction of the Member State in which they are established.",
        "plain_english": "You are subject to NIS2 in the EU country where you are established — for certain digital services, it's where your main EU establishment is.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "primary_jurisdiction", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "jurisdiction", "establishment"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Identify which EU member state has jurisdiction over your NIS2 obligations based on your main establishment.",
    },
    {
        "article": "Article 27", "article_number": 27,
        "title": "Register of essential and important entities",
        "chapter": "Chapter IV — Jurisdiction and Registration", "category": "Registration",
        "description": "Member States shall establish a register of essential and important entities and entities providing domain name registration services. Entities shall submit to the competent authority at least the following information: name, address, registration number; sector and subsector; list of Member States where they provide services; contact details including email, phone; IP ranges; and date of submission. Entities shall update information without undue delay, and at least every two years.",
        "plain_english": "You must register with your national NIS2 authority and keep your information up to date — including contact details, sector, and IP ranges.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "policy_required",
        "profile_field": "nis2_data.nis2_sectors",
        "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "registration", "competent_authority"],
        "evaluation_logic": {"type": "policy_required", "required_policies": ["nis2_registration_completed"]},
        "remediation_hint": "Register with your national NIS2 competent authority. Update your registration at least every 2 years or when information changes.",
    },
    {
        "article": "Article 28", "article_number": 28,
        "title": "Database of domain name registration data",
        "chapter": "Chapter IV — Jurisdiction and Registration", "category": "Registration",
        "description": "TLD name registries and entities providing domain name registration services shall collect and maintain accurate and complete domain name registration data in a dedicated database with due diligence in accordance with Union data protection law. The database shall contain information necessary to identify and contact the holders of the domain names and the points of contact administering the domain names.",
        "plain_english": "Domain name registries and registrars must maintain accurate WHOIS-style databases with domain holder contact details.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "domain_registration", "DNS", "WHOIS"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Applies specifically to TLD registries and domain registrars — ensure accurate domain registration data is maintained.",
    },

    # Chapter V — Union Level Cybersecurity
    {
        "article": "Article 29", "article_number": 29,
        "title": "Cybersecurity information sharing arrangements",
        "chapter": "Chapter V — Union Level Cybersecurity", "category": "Information Sharing",
        "description": "Member States shall ensure that essential and important entities and, where relevant, their suppliers or service providers, may exchange relevant cybersecurity information among themselves on a voluntary basis, including information relating to cyber threats, near misses, vulnerabilities, techniques and procedures, indicators of compromise, and cybersecurity tools. Such sharing shall be carried out through sharing arrangements with the aim of preventing, detecting, responding to, or recovering from incidents.",
        "plain_english": "Organisations are encouraged to voluntarily share cyber threat intelligence and incident information with peers to improve collective defence.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "information_sharing", "threat_intelligence"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Consider joining sector-specific Information Sharing and Analysis Centres (ISACs) or other threat intelligence sharing communities.",
    },
    {
        "article": "Article 30", "article_number": 30,
        "title": "Voluntary notification of relevant information",
        "chapter": "Chapter V — Union Level Cybersecurity", "category": "Information Sharing",
        "description": "Member States shall ensure that entities that are not essential or important entities under NIS2 may voluntarily notify significant incidents, cyber threats and near misses to the competent authority or CSIRT. Voluntary notifications shall not result in the imposition of additional obligations on the notifying entity that would not have been imposed had it not submitted the notification.",
        "plain_english": "Even if NIS2 doesn't apply to you, you can voluntarily report cyber incidents and threats to national authorities without triggering additional obligations.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "voluntary_notification"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Consider voluntarily reporting significant cyber incidents even if outside NIS2 mandatory scope — it helps national threat intelligence.",
    },

    # Chapter VI — Supervisory and Enforcement
    {
        "article": "Article 31", "article_number": 31,
        "title": "General aspects of supervision and enforcement",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "Member States shall ensure competent authorities effectively supervise and take necessary measures to ensure compliance with NIS2. Competent authorities shall cooperate with each other, with the Commission, and with ENISA. Supervision shall be proportionate and risk-based. For essential entities, proactive supervision applies; for important entities, supervision is reactive (after indication of non-compliance).",
        "plain_english": "Essential entities face regular proactive audits and inspections; important entities are only investigated when there's evidence of non-compliance.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "nis2_data.entity_type", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "supervision", "enforcement", "essential_entity", "important_entity"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Essential entities should prepare for proactive regulatory audits. Maintain audit-ready documentation of your cybersecurity measures.",
    },
    {
        "article": "Article 32", "article_number": 32,
        "title": "Supervisory and enforcement measures in relation to essential entities",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "For essential entities, competent authorities shall have powers to: conduct on-site inspections and remote supervision; carry out security audits; request information and documentation; issue warnings; issue binding instructions; require entities to implement security measures; require entities to inform users of threats; designate a monitoring officer; temporarily suspend or request judicial suspension of a service or activity; and impose administrative fines. Competent authorities may require essential entities to make a public declaration regarding non-compliance.",
        "plain_english": "For essential entities, authorities can audit, inspect, issue binding instructions, suspend services, and impose fines up to €10M or 2% of global turnover.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "nis2_data.entity_type", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "enforcement", "essential_entity", "fines", "suspension"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "If classified as essential, maintain comprehensive compliance documentation ready for proactive supervisory audits.",
    },
    {
        "article": "Article 33", "article_number": 33,
        "title": "Supervisory and enforcement measures in relation to important entities",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "For important entities, competent authorities shall have the same supervisory powers as for essential entities except that supervision is reactive rather than proactive. Important entities are subject to supervision only after receiving an indication of non-compliance, or on the basis of information, specific requests, notifications, or complaints. Fines for important entities: up to €7M or 1.4% of total worldwide annual turnover.",
        "plain_english": "Important entities are only investigated when there's a complaint or indication of non-compliance — fines up to €7M or 1.4% of global turnover.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "nis2_data.entity_type", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "enforcement", "important_entity", "fines"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Important entities should still implement all NIS2 measures — reactive supervision means you'll be investigated if something goes wrong.",
    },
    {
        "article": "Article 34", "article_number": 34,
        "title": "General rules on administrative fines",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Fines",
        "description": "Member States shall ensure that administrative fines for essential and important entities are effective, proportionate and dissuasive. Essential entities: maximum fine of at least €10,000,000 or 2% of total worldwide annual turnover, whichever is higher. Important entities: maximum fine of at least €7,000,000 or 1.4% of total worldwide annual turnover, whichever is higher. Management bodies of essential entities can be held personally liable and temporarily banned from management roles for repeated infringements.",
        "plain_english": "NIS2 fines: essential entities up to €10M or 2% global turnover; important entities up to €7M or 1.4% global turnover. Management can be personally fined and banned.",
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": "nis2_data.entity_type", "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "fines", "penalties", "management_liability"],
        "evaluation_logic": {"type": "informational", "essential_max": "€10M or 2% global turnover", "important_max": "€7M or 1.4% global turnover"},
        "remediation_hint": "Prioritise NIS2 compliance — fines and personal management liability make non-compliance extremely costly.",
    },
    {
        "article": "Article 35", "article_number": 35,
        "title": "Infringements entailing a personal data breach",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "Where a NIS2 infringement also constitutes a personal data breach under GDPR, competent authorities and data protection authorities shall cooperate to ensure consistent enforcement. Fines under NIS2 and GDPR shall not be cumulative for the same conduct — the higher fine shall apply. Competent authorities shall inform data protection authorities where a NIS2 infringement results in a personal data breach.",
        "plain_english": "If a cyber incident is also a GDPR data breach, you won't be double-fined — only the higher of the NIS2 or GDPR fine applies.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "GDPR", "personal_data_breach", "double_fining"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Coordinate your NIS2 incident reporting and GDPR breach notification processes — a single incident may trigger both.",
    },
    {
        "article": "Article 36", "article_number": 36,
        "title": "Penalties",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Fines",
        "description": "Member States shall lay down rules on penalties applicable to infringements of national measures adopted pursuant to this Directive and shall take all measures necessary to ensure that they are implemented. Penalties shall be effective, proportionate and dissuasive. Member States shall notify the Commission of those rules and of any subsequent amendment thereto without delay.",
        "plain_english": "EU countries implement NIS2 penalties in national law — these must be effective, proportionate, and dissuasive.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "penalties", "national_law"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Check your country's national NIS2 implementation law for specific penalty provisions beyond the EU minimums.",
    },
    {
        "article": "Article 37", "article_number": 37,
        "title": "Mutual assistance",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "At the request of a competent authority, other competent authorities may provide assistance with supervisory or enforcement actions concerning cross-border service providers. Requests for mutual assistance shall be proportionate. Requested authorities shall respond within one month and carry out the requested measures using their supervisory powers. Reasons must be given if assistance cannot be provided.",
        "plain_english": "EU supervisory authorities assist each other in cross-border NIS2 enforcement cases.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "mutual_assistance", "cross_border"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — relevant if subject to cross-border NIS2 supervision.",
    },
    {
        "article": "Article 38", "article_number": 38,
        "title": "Joint supervisory actions",
        "chapter": "Chapter VI — Supervisory and Enforcement", "category": "Enforcement",
        "description": "Competent authorities of two or more Member States may carry out joint supervisory actions. The competent authority of the Member State in which the entity is established shall lead the joint action. Joint actions may be proposed by any participating competent authority.",
        "plain_english": "Multiple EU supervisory authorities can conduct joint investigations and audits of cross-border entities.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "joint_supervision", "cross_border"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Cross-border organisations should prepare for coordinated multi-country regulatory inspections.",
    },

    # Chapter VII — Delegated and Implementing Acts
    {
        "article": "Article 39", "article_number": 39,
        "title": "Exercise of the delegation",
        "chapter": "Chapter VII — Delegated and Implementing Acts", "category": "Legislative",
        "description": "The power to adopt delegated acts is conferred on the Commission for a period of five years from 17 January 2023. The European Parliament or the Council may revoke the delegation at any time.",
        "plain_english": "The Commission can adopt supplementary NIS2 implementing rules for a renewable five-year period.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "delegated_acts"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Monitor EU Official Journal for NIS2 delegated acts that may introduce new requirements.",
    },
    {
        "article": "Article 40", "article_number": 40,
        "title": "Committee procedure",
        "chapter": "Chapter VII — Delegated and Implementing Acts", "category": "Legislative",
        "description": "The Commission shall be assisted by a committee. Where reference is made to this Article, the examination procedure referred to in Article 5 of Regulation (EU) No 182/2011 shall apply.",
        "plain_english": "The Commission uses a standard EU committee procedure when adopting NIS2 implementing measures.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "implementing_acts"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Informational — no direct action required for organisations.",
    },

    # Chapter VIII — Transitional and Final Provisions
    {
        "article": "Article 41", "article_number": 41,
        "title": "Review",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "By 17 October 2027 and every 36 months thereafter, the Commission shall review the functioning of this Directive and report to the European Parliament and the Council. The review shall assess whether the scope of this Directive should be extended, whether additional sectors or subsectors should be covered, and whether the supervisory framework is effective.",
        "plain_english": "The Commission reviews NIS2 every 3 years from 2027 and may expand its scope to additional sectors.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "review", "legislative"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Monitor NIS2 review outcomes — additional sectors may come into scope from 2027 onwards.",
    },
    {
        "article": "Article 42", "article_number": 42,
        "title": "Amendments to Regulation (EU) No 910/2014",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "Regulation (EU) No 910/2014 (eIDAS) is amended to align trust service providers with NIS2 security requirements. Trust service providers are subject to NIS2 obligations for cybersecurity risk management and incident reporting.",
        "plain_english": "NIS2 aligns the eIDAS Regulation (electronic signatures and trust services) with NIS2 cybersecurity requirements.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "eIDAS", "trust_services"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "If you are an eIDAS trust service provider, ensure compliance with both eIDAS and NIS2 cybersecurity requirements.",
    },
    {
        "article": "Article 43", "article_number": 43,
        "title": "Amendments to Directive (EU) 2018/1972",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "Directive (EU) 2018/1972 (European Electronic Communications Code) is amended to align providers of public electronic communications networks and services with NIS2 security and incident reporting obligations.",
        "plain_english": "NIS2 aligns telecom provider cybersecurity obligations with the NIS2 framework.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "telecoms", "electronic_communications"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Applies to electronic communications providers — align cybersecurity obligations under both NIS2 and the EECC.",
    },
    {
        "article": "Article 44", "article_number": 44,
        "title": "Repeal",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "Directive (EU) 2016/1148 (NIS1) is repealed with effect from 18 October 2024. References to the repealed Directive shall be construed as references to this Directive.",
        "plain_english": "NIS1 (the original 2016 cybersecurity directive) was replaced by NIS2 on 18 October 2024.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "NIS1", "repeal"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Ensure all internal policies reference NIS2 (2022/2555) and not the old NIS1 directive.",
    },
    {
        "article": "Article 45", "article_number": 45,
        "title": "Transposition",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "Member States shall adopt and publish, by 17 October 2024, the measures necessary to comply with this Directive. Member States shall apply those measures from 18 October 2024. Member States shall communicate to the Commission the text of the measures of national law which they adopt in the field covered by this Directive.",
        "plain_english": "EU countries had to implement NIS2 into national law by 17 October 2024, with application from 18 October 2024.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "transposition", "national_law"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "Check your country's national NIS2 implementation law — requirements may go beyond the EU minimum.",
    },
    {
        "article": "Article 46", "article_number": 46,
        "title": "Entry into force",
        "chapter": "Chapter VIII — Transitional and Final Provisions", "category": "Legislative",
        "description": "This Directive shall enter into force on the twentieth day following that of its publication in the Official Journal of the European Union. It was published on 27 December 2022 and entered into force on 16 January 2023. Member States were required to transpose it by 17 October 2024.",
        "plain_english": "NIS2 entered into force on 16 January 2023 and became applicable in member states from 18 October 2024.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": "informational",
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ["NIS2", "entry_into_force"],
        "evaluation_logic": {"type": "informational"},
        "remediation_hint": "NIS2 has been fully applicable since 18 October 2024 — ensure compliance now.",
    },
]


# ── Seeder ────────────────────────────────────────────────────────────────────

async def seed() -> None:
    async with SessionLocal() as session:
        existing = await session.execute(
            select(Regulation).where(Regulation.name == "NIS2")
        )
        if existing.scalar_one_or_none():
            print("✓ NIS2 already seeded — skipping.")
            return

        await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        regulation = Regulation(**NIS2_REGULATION)
        session.add(regulation)
        await session.flush()

        version = RegulationVersion(regulation_id=regulation.id, **NIS2_VERSION)
        session.add(version)
        await session.flush()

        for data in NIS2_ARTICLES:
            session.add(Rule(
                regulation_id=regulation.id,
                regulation_version_id=version.id,
                **data,
            ))

        await session.commit()
        print(f"✅ NIS2 seeded: 1 regulation, 1 version, {len(NIS2_ARTICLES)} articles.")


if __name__ == "__main__":
    asyncio.run(seed())
