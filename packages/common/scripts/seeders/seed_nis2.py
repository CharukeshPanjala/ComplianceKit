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
        "article": 'Article 1', "article_number": 1,
        "title": 'Subject matter',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": 'This Directive lays down measures aimed at achieving a high common level of cybersecurity across the Union, with a view to improving the functioning of the internal market. It establishes obligations for Member States to adopt national cybersecurity strategies, designate competent authorities, establish CSIRTs, and adopt supervisory and enforcement measures.',
        "plain_english": 'NIS2 sets the framework for cybersecurity across the EU — requiring governments to have strategies, authorities, and incident response teams, and requiring organisations to meet security standards.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'general', 'scope'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Understand whether NIS2 applies to your organisation based on sector and size thresholds.',
    },
    {
        "article": 'Article 2', "article_number": 2,
        "title": 'Scope',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": 'This Directive applies to public or private entities of a type referred to in Annexes I and II that qualify as medium-sized enterprises under Article 2 of the Annex to Recommendation 2003/361/EC, or exceed the ceilings for medium-sized enterprises, and which provide their services or carry out their activities within the Union. Essential sectors (Annex I): energy, transport, banking, financial market infrastructure, health, drinking water, wastewater, digital infrastructure, ICT service management, public administration, space. Important sectors (Annex II): postal and courier services, waste management, manufacture/production and distribution of chemicals, food production, manufacturing, digital providers, research.',
        "plain_english": 'NIS2 applies to medium and large organisations in 18 critical sectors. Small companies (under 50 employees, under €10M turnover) are generally exempt unless they are sole providers of critical services.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.sectors', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'scope', 'essential_entities', 'important_entities', 'sectors'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.sectors is not empty AND meets size threshold'},
        "remediation_hint": 'Assess whether your organisation falls within NIS2 scope based on sector (Annex I/II) and size. Register with your national competent authority if in scope.',
    },
    {
        "article": 'Article 3', "article_number": 3,
        "title": 'Essential and important entities',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": 'Entities shall be considered essential entities if they: are large enterprises in Annex I sectors; are certain categories of public administration; are qualified trust service providers, TLD name registries, DNS service providers, or certain domain name registration entities; are sole providers of a service essential for society/economy; or are identified by Member States due to their critical nature. All other entities in Annex I and II that do not qualify as essential are important entities. Essential entities face stricter supervision than important entities.',
        "plain_english": 'Essential entities (stricter rules, proactive supervision) vs important entities (lighter touch, reactive supervision) — your classification determines your compliance obligations and fine exposure.',
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.entity_type', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'essential_entity', 'important_entity', 'classification'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.entity_type is defined'},
        "remediation_hint": 'Determine whether your organisation qualifies as essential or important. Essential entities face proactive supervision; important entities face reactive supervision.',
    },
    {
        "article": 'Article 4', "article_number": 4,
        "title": 'Sector-specific Union legal acts',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": 'Where sector-specific Union legal acts require essential or important entities to adopt cybersecurity risk-management measures or to notify significant incidents, and where those requirements are at least equivalent in effect to the obligations laid down in this Directive, the relevant provisions of this Directive shall not apply to those entities. NIS2 acts as a cybersecurity baseline; sector-specific rules (e.g. DORA for financial sector) may take precedence where they are equivalent or stricter.',
        "plain_english": 'If your sector has its own EU cybersecurity law (e.g. DORA for finance, NIS2 for energy), those sector-specific rules apply instead of NIS2 where equivalent.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'industry', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'sector_specific', 'DORA', 'lex_specialis'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Check whether your sector has specific EU cybersecurity legislation (e.g. DORA for financial entities) that may supplement or replace some NIS2 obligations.',
    },
    {
        "article": 'Article 5', "article_number": 5,
        "title": 'Minimum harmonisation',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": "This Directive does not prevent Member States from adopting or maintaining provisions ensuring a higher level of cybersecurity, provided that such provisions are consistent with Member States' obligations under Union law.",
        "plain_english": "EU countries can set stricter cybersecurity rules than NIS2's minimum, as long as those stricter rules still comply with other EU law.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'minimum_harmonisation', 'general'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — no direct action required for organisations.',
    },
    {
        "article": 'Article 6', "article_number": 6,
        "title": 'Definitions',
        "chapter": 'Chapter I — General Provisions', "category": 'General',
        "description": 'For the purposes of this Directive, the following definitions apply: "network and information system" means an electronic communications network, any device or group of interconnected devices which carry out automatic processing of digital data, or digital data stored, processed, retrieved, or transmitted by the above elements for the purpose of their operation, use, protection, and maintenance; "security of network and information systems" means the ability of network and information systems to resist, at a given level of confidence, any event that may compromise the availability, authenticity, integrity, or confidentiality of stored, transmitted, or processed data or of the related services; "national cybersecurity strategy" means a coherent framework of a Member State providing strategic objectives and priorities in the area of cybersecurity and the governance to achieve them; "near miss" means an event that could have compromised the availability, authenticity, integrity, or confidentiality of stored, transmitted, or processed data or of the services offered by, or accessible via, network and information systems, but that was successfully prevented from materialising or that did not materialise; "incident" means an event compromising the availability, authenticity, integrity, or confidentiality of stored, transmitted, or processed data or of the services offered by, or accessible via, network and information systems; "large-scale cybersecurity incident" means an incident which causes a level of disruption that exceeds a Member State\'s capacity to respond to it or which has a significant impact on at least two Member States; "incident handling" means any actions and procedures aiming to prevent, detect, analyse, and contain or to respond to and recover from an incident; "risk" means the potential for loss or disruption caused by an incident, expressed as a combination of the magnitude of such loss or disruption and the likelihood of occurrence of the incident; "cyber threat" has the meaning given in Article 2, point (8), of Regulation (EU) 2019/881; "significant cyber threat" means a cyber threat which, based on its technical characteristics, can be assumed to have the potential to have a severe impact on the network and information systems of an entity or the users of the entity\'s services by causing considerable material or non-material damage; "ICT product", "ICT service", and "ICT process" have the meanings given in Article 2, points (12), (13), and (14), of Regulation (EU) 2019/881; "vulnerability" means a weakness, susceptibility, or flaw of ICT products or ICT services that can be exploited by a cyber threat; further definitions cover standard, technical specification, internet exchange point, domain name system (DNS), DNS service provider, top-level domain name registry, entity providing domain name registration services, digital service, trust service and qualified trust service (by reference to Regulation (EU) No 910/2014), online marketplace, online search engine, cloud computing service, data centre service, content delivery network, social networking services platform, representative, public administration entity, public electronic communications network and electronic communications service (by reference to Directive (EU) 2018/1972), entity, managed service provider, managed security service provider, and research organisation.',
        "plain_english": 'This article defines the key terms used throughout NIS2, including incident, near miss, cyber threat, vulnerability, and the different categories of digital infrastructure and service providers the law applies to.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'definitions', 'general'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — no direct action required for organisations.',
    },

    # Chapter II — Coordinated Cybersecurity Frameworks
    {
        "article": 'Article 7', "article_number": 7,
        "title": 'National cybersecurity strategy',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'National Framework',
        "description": 'Each Member State shall adopt a national cybersecurity strategy covering: objectives and priorities; governance framework; measures on preparedness, response, and recovery; education, awareness, and training; research and development priorities; measures to address supply chain cybersecurity risks; measures to promote and develop national cybersecurity industry; and international cooperation. Strategies shall be reviewed at least every five years.',
        "plain_english": 'Every EU country must have a national cybersecurity strategy covering prevention, response, and education — reviewed every 5 years.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'national_strategy', 'government'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Review your national cybersecurity strategy to understand government priorities and align your own security programme.',
    },
    {
        "article": 'Article 8', "article_number": 8,
        "title": 'Competent authorities and single points of contact',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'National Framework',
        "description": 'Each Member State shall designate one or more competent authorities responsible for cybersecurity and the supervisory tasks under this Directive. Member States shall designate a single point of contact to exercise a liaison function to ensure cross-border cooperation of Member State authorities. Member States may designate an existing authority as competent authority and single point of contact.',
        "plain_english": 'Each EU country designates a national cybersecurity authority and a single point of contact for cross-border cooperation — this is who you report incidents to.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'competent_authority', 'reporting'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Identify your national NIS2 competent authority — this is where you register and report incidents.',
    },
    {
        "article": 'Article 9', "article_number": 9,
        "title": 'National cyber crisis management frameworks',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'National Framework',
        "description": 'Each Member State shall designate one or more competent authorities responsible for cyber crisis management. Member States shall designate a national cyber crisis management authority and identify capabilities, assets, and procedures that can be deployed in cases of large-scale cybersecurity incidents and crises. Cooperation between civil and criminal authorities on cybersecurity shall be ensured.',
        "plain_english": 'Each EU country must have a cyber crisis management framework with designated authorities for handling large-scale cybersecurity incidents.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'crisis_management', 'government'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Know your national cyber crisis management authority and their escalation procedures for large-scale incidents.',
    },
    {
        "article": 'Article 10', "article_number": 10,
        "title": 'Computer security incident response teams (CSIRTs)',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'National Framework',
        "description": 'Each Member State shall designate one or more CSIRTs (Computer Security Incident Response Teams). CSIRTs may be established within a competent authority. CSIRTs shall have adequate resources and technical capabilities. CSIRTs shall be available 24/7 and their contact information shall be made publicly available. CSIRTs shall monitor and analyse cybersecurity threats, vulnerabilities and incidents at national level.',
        "plain_english": 'Every EU country must have 24/7 Computer Security Incident Response Teams (CSIRTs) that monitor threats and help entities respond to incidents.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'CSIRT', 'incident_response'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Know your national CSIRT contact details. In a cyber incident, your CSIRT is a resource for technical assistance and threat intelligence.',
    },
    {
        "article": 'Article 11', "article_number": 11,
        "title": 'Requirements, technical capabilities and tasks of CSIRTs',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'National Framework',
        "description": 'CSIRTs shall meet the following requirements: have a high level of availability of communication channels; be located in a secure facility; be equipped with a backup system; have staff with relevant skills; be subject to IT security quality management; operate on a 24/7 basis; participate in EU-level cooperation networks. CSIRTs shall have well-defined processes for handling incidents and maintaining confidentiality of vulnerability information.',
        "plain_english": 'National CSIRTs must meet specific technical and operational standards including 24/7 availability and secure infrastructure.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'CSIRT', 'requirements'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — directly applies to government CSIRTs, not private organisations.',
    },
    {
        "article": 'Article 12', "article_number": 12,
        "title": 'Coordinated vulnerability disclosure and a European vulnerability database',
        "chapter": 'Chapter II — Coordinated Cybersecurity Frameworks', "category": 'Vulnerability Management',
        "description": 'Member States shall designate a CSIRT as coordinator for coordinated vulnerability disclosure. ENISA shall establish and maintain a European vulnerability database for publicly known vulnerabilities in ICT products and ICT services, accessible to the public. ENISA shall adopt adequate technical and organisational measures to ensure the security of the database. To support this process, Member States shall also take the necessary measures to allow security researchers to report vulnerabilities they have discovered under legal protection, with CSIRTs acting as trusted intermediaries between reporting researchers and the manufacturers or providers of the affected ICT products or services.',
        "plain_english": 'EU countries must have a coordinated vulnerability disclosure process, including a European vulnerability database maintained by ENISA, and must legally protect security researchers who responsibly report vulnerabilities they find.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": 'profile_field',
        "profile_field": 'nis2_data.has_vulnerability_disclosure_policy', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'vulnerability_disclosure', 'ENISA', 'security_researchers'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.has_vulnerability_disclosure_policy == true'},
        "remediation_hint": "Monitor ENISA's European vulnerability database and your national CSIRT's coordinated vulnerability disclosure programme.",
    },

    # Chapter III — Cybersecurity Risk Management and Reporting
    {
        "article": 'Article 13', "article_number": 13,
        "title": 'National-level cooperation',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Cooperation',
        "description": 'Where the competent authority or authorities, the single point of contact, and the CSIRT or CSIRTs of a Member State are separate entities, they shall cooperate with each other regarding the fulfilment of the obligations laid down in this Directive. Member States shall ensure that either their competent authorities or their CSIRTs receive notifications of significant incidents (Article 23) and of incidents, cyber threats, and near misses (Article 30). Member States shall ensure that their CSIRTs or, where applicable, their competent authorities inform their single points of contact about notifications of incidents, cyber threats, and near misses submitted pursuant to this Directive. In order for the obligations of the competent authorities, single points of contact, and CSIRTs to be fulfilled effectively, Member States shall ensure, to the extent possible, appropriate cooperation between those bodies and law enforcement authorities, data protection authorities, the national authorities under Regulation (EC) No 300/2008 and Regulation (EU) 2018/1139, the authorities responsible under the Digital Operational Resilience Act (Regulation (EU) 2022/2554), the national regulatory authorities under Directive (EU) 2018/1972, and the competent authorities under the Critical Entities Resilience Directive (EU) 2022/2557, within that Member State.',
        "plain_english": 'Within each EU country, the cybersecurity authority, the single point of contact, and the national CSIRT must coordinate with each other and with related authorities like data protection regulators and law enforcement when handling NIS2 obligations.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'cooperation', 'NIS_Cooperation_Group'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — government-level cooperation framework.',
    },
    {
        "article": 'Article 14', "article_number": 14,
        "title": 'Cooperation Group',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Cooperation',
        "description": 'A NIS Cooperation Group is established to support and facilitate strategic cooperation and the exchange of information among Member States and to develop trust and confidence. It shall be composed of representatives of Member States, the Commission and ENISA. Tasks include providing strategic guidance to the CSIRTs network, exchanging best practices on national cybersecurity strategies, and assisting Member States in building cybersecurity capabilities.',
        "plain_english": 'The NIS Cooperation Group brings together EU governments and ENISA to share cybersecurity strategy and best practices.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'NIS_Cooperation_Group', 'ENISA'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Follow NIS Cooperation Group publications for guidance on national and EU-level cybersecurity priorities.',
    },
    {
        "article": 'Article 15', "article_number": 15,
        "title": 'CSIRTs network',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Cooperation',
        "description": 'A network of national CSIRTs is established. The CSIRTs network shall contribute to building confidence and trust between Member States and promote swift and effective operational cooperation. Tasks include exchanging information on incidents, threats and vulnerabilities; coordinating responses to cross-border incidents; and providing mutual assistance.',
        "plain_english": 'EU national CSIRTs form a network to share threat intelligence and coordinate cross-border incident responses.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'CSIRT', 'network', 'cooperation'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — your national CSIRT participates in EU-wide threat intelligence sharing.',
    },
    {
        "article": 'Article 16', "article_number": 16,
        "title": 'European cyber crises liaison organisation network (EU-CyCLONe)',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Crisis Management',
        "description": 'Member States shall establish an EU-CyCLONe network to support coordinated management of large-scale cybersecurity incidents and crises at operational level. EU-CyCLONe shall be composed of representatives of Member State cyber crisis management authorities and the Commission. EU-CyCLONe shall build capability and preparedness for large-scale cybersecurity incidents and crises that may have a significant cross-border impact.',
        "plain_english": 'The EU has a network (EU-CyCLONe) to coordinate responses to large-scale cross-border cybersecurity incidents.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'EU_CyCLONe', 'crisis_management'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — EU-CyCLONe is a government-level coordination body.',
    },
    {
        "article": 'Article 17', "article_number": 17,
        "title": 'International cooperation',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Cooperation',
        "description": 'The Union may conclude international agreements with third countries or international organisations allowing and organising their participation in certain activities of the NIS Cooperation Group and the CSIRTs network. Such agreements shall ensure adequate protection of personal data.',
        "plain_english": 'The EU can form international cybersecurity cooperation agreements with non-EU countries.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'international_cooperation'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — relevant if operating in non-EU countries with international NIS2 cooperation agreements.',
    },
    {
        "article": 'Article 18', "article_number": 18,
        "title": 'Report on the state of cybersecurity in the Union',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Reporting',
        "description": "ENISA shall, in cooperation with the Commission and the Cooperation Group, adopt a biennial report on the state of cybersecurity in the Union and submit that report to the European Parliament. The report shall, among other things, be made available in a machine-readable format and shall include: (a) an assessment of the development of cybersecurity capabilities across the Union; (b) an assessment of the level of cybersecurity awareness and cyber hygiene among citizens and entities, including small and medium enterprises; (c) an aggregated assessment of the results of peer reviews referred to in Article 19; (d) an aggregated assessment of the level of maturity of cybersecurity capabilities and resources across the Union, including at sector level, and of the extent to which national cybersecurity strategies are aligned. The report shall include specific policy recommendations to address shortcomings and raise the level of cybersecurity across the Union, and a summary of the findings from ENISA's biennial technical EU cybersecurity situation reports on incidents and cyber threats. ENISA shall develop the methodology, including relevant variables (quantitative and qualitative indicators), for the assessment referred to above, in cooperation with the Commission, the Cooperation Group, and the CSIRTs network.",
        "plain_english": 'Every two years, ENISA publishes a report on the overall state of cybersecurity across the EU, covering capability levels, public awareness, and policy recommendations. This is a government/EU-level reporting obligation, not something your organisation needs to act on directly.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'ENISA', 'biennial_report', 'cybersecurity_state'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Implement a 3-stage incident reporting workflow: 24h early warning, 72h notification, 1-month final report. Pre-register with your national competent authority.',
    },
    {
        "article": 'Article 19', "article_number": 19,
        "title": 'Peer reviews',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Cooperation',
        "description": "The NIS Cooperation Group shall organise peer reviews with the aim of learning from shared experiences, strengthening mutual trust, achieving a high common level of cybersecurity and enhancing Member States' cybersecurity capabilities and policies. Peer reviews shall be carried out by cybersecurity experts designated by Member States.",
        "plain_english": 'EU countries conduct mutual peer reviews of their cybersecurity capabilities to learn from each other.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'peer_review'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — government-level peer reviews.',
    },
    {
        "article": 'Article 20', "article_number": 20,
        "title": 'Governance',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Governance',
        "description": 'Member States shall ensure that the management bodies of essential and important entities approve the cybersecurity risk-management measures taken by those entities pursuant to Article 21, oversee its implementation, and can be held liable for infringements. Management bodies are required to follow cybersecurity training and to encourage entities to offer similar training to their employees on a regular basis to gain sufficient knowledge and skills to identify risks and assess cybersecurity risk-management practices and their impact on services.',
        "plain_english": 'Your board/management body must approve and oversee cybersecurity measures, undergo cybersecurity training, and can be held personally liable for NIS2 violations.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.management_approved_security_measures', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'governance', 'management_liability', 'board', 'training'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.management_approved_security_measures == true'},
        "remediation_hint": 'Ensure your board formally approves your cybersecurity risk management framework and undertakes regular cybersecurity training. Document their involvement.',
    },
    {
        "article": 'Article 21', "article_number": 21,
        "title": 'Cybersecurity risk-management measures',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Risk Management',
        "description": 'Member States shall ensure that essential and important entities take appropriate and proportionate technical, operational and organisational measures to manage cybersecurity risks. Measures shall be based on an all-hazards approach and include at minimum: (a) risk analysis and information system security policies; (b) incident handling; (c) business continuity (backups, disaster recovery, crisis management); (d) supply chain security including third-party relationships; (e) security in network and information systems acquisition, development and maintenance including vulnerability handling and disclosure; (f) policies and procedures to assess the effectiveness of cybersecurity risk-management measures; (g) basic cyber hygiene practices and cybersecurity training; (h) policies and procedures regarding the use of cryptography and encryption; (i) human resources security, access control policies and asset management; (j) use of multi-factor authentication (MFA), continuous authentication solutions, secured voice/video/text communications, and secured emergency communications.',
        "plain_english": 'The core NIS2 obligation — implement 10 minimum cybersecurity measures including risk management, incident response, BCP, supply chain security, encryption, MFA, and regular training.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.has_mfa', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'risk_management', 'security_measures', 'MFA', 'encryption', 'BCP', 'supply_chain'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data composite security measures score'},
        "remediation_hint": 'Implement all 10 minimum NIS2 security measures. Use ISO 27001 or CIS Controls as a framework. Prioritise MFA, BCP, incident response, and supply chain security.',
    },
    {
        "article": 'Article 22', "article_number": 22,
        "title": 'Union level coordinated security risk assessments of critical supply chains',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Supply Chain',
        "description": 'The NIS Cooperation Group, in cooperation with the Commission and ENISA, may carry out coordinated security risk assessments of specific critical ICT services, ICT systems or ICT products supply chains. These assessments shall take into account technical and non-technical risk factors, and shall identify mitigation measures. The results shall inform Member State policies and guidance for essential and important entities.',
        "plain_english": 'The EU coordinates supply chain security risk assessments for critical ICT products and services — results feed into guidance for organisations.',
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'supply_chain', 'risk_assessment'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Monitor EU coordinated supply chain risk assessment results — especially for 5G, cloud, and critical software supply chains.',
    },
    {
        "article": 'Article 23', "article_number": 23,
        "title": 'Reporting obligations',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Incident Reporting',
        "description": 'Essential and important entities shall notify their CSIRT or competent authority of significant incidents without undue delay. A significant incident is one that has caused or is capable of causing severe operational disruption or financial loss to the entity concerned; or affected or is capable of affecting other natural or legal persons by causing considerable material or non-material damage. Notification timeline: without undue delay and in any event within 24 hours of becoming aware (early warning); within 72 hours of becoming aware (incident notification with initial assessment); upon request, an intermediate report; within one month of the incident notification (final report with full details). Entities shall also notify recipients of their services of significant incidents that are likely to adversely affect the provision of those services.',
        "plain_english": 'Mandatory reporting timeline for significant incidents: 24h early warning → 72h notification → 1-month final report. Also notify affected customers.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.has_incident_response_plan', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'incident_reporting', 'significant_incident', '24h', '72h', 'notification'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.has_incident_response_plan == true', 'deadline_hours': 24},
        "remediation_hint": "Build a 3-stage incident reporting process with pre-drafted notification templates. Test it in tabletop exercises. Know your national competent authority's reporting portal.",
    },
    {
        "article": 'Article 24', "article_number": 24,
        "title": 'Use of European cybersecurity certification schemes',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Certification',
        "description": 'Member States may require essential and important entities to use particular ICT products, ICT services, and ICT processes, developed by the essential or important entity or procured from third parties, that are certified under European cybersecurity certification schemes adopted pursuant to Article 49 of Regulation (EU) 2019/881, in order to demonstrate compliance with the cybersecurity risk-management requirements under Article 21. Member States shall also encourage essential and important entities to use qualified trust services. The Commission is empowered to adopt delegated acts, in accordance with Article 38, to supplement this Directive by specifying which categories of essential and important entities shall be required to use certain certified ICT products, ICT services, and ICT processes or to obtain a certificate under a European cybersecurity certification scheme adopted pursuant to Article 49 of Regulation (EU) 2019/881. Such delegated acts shall be adopted where an insufficient level of cybersecurity has been identified, and shall include an implementation period. Before adopting such delegated acts, the Commission shall carry out an impact assessment and conduct consultations in accordance with Article 56 of Regulation (EU) 2019/881. Where no appropriate European cybersecurity certification scheme is available for the purposes referred to above, the Commission may, after consulting the Cooperation Group and the European Cybersecurity Certification Group, request ENISA to prepare a possible scheme pursuant to Article 48(2) of Regulation (EU) 2019/881.',
        "plain_english": "EU countries can require organisations to use cybersecurity-certified ICT products and services to prove they meet NIS2's risk-management standards. The EU can also make specific certifications mandatory for certain types of organisations if security gaps are found.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": 'profile_field',
        "profile_field": 'nis2_data.uses_certified_products', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'certification', 'EU_Cybersecurity_Act', 'delegated_acts'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.uses_certified_products == true'},
        "remediation_hint": "Use ENISA's incident reporting guidelines and templates to ensure your notifications meet NIS2 requirements.",
    },
    {
        "article": 'Article 25', "article_number": 25,
        "title": 'Standardisation',
        "chapter": 'Chapter III — Cybersecurity Risk Management and Reporting', "category": 'Standardisation',
        "description": "In order to promote the convergent implementation of Article 21(1) and (2), Member States shall, without imposing or discriminating in favour of the use of a particular type of technology, encourage the use of European and international standards and technical specifications relevant to the security of network and information systems. ENISA, in cooperation with Member States, shall draw up advice and guidelines regarding the technical areas to be considered in relation to the first paragraph, as well as regarding already existing standards, including Member States' national standards, which would allow for those areas to be covered.",
        "plain_english": "EU countries encourage (without mandating any specific vendor or technology) the use of recognised European and international cybersecurity standards, like ISO 27001, to help organisations meet NIS2's security requirements consistently.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'standardisation', 'ENISA', 'ISO_27001'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Include customer notification steps in your incident response plan with pre-approved communication templates.',
    },

    # Chapter IV — Jurisdiction and Registration
    {
        "article": 'Article 26', "article_number": 26,
        "title": 'Jurisdiction and territoriality',
        "chapter": 'Chapter IV — Jurisdiction and Registration', "category": 'Jurisdiction',
        "description": 'Essential and important entities shall be deemed to fall under the jurisdiction of the Member State in which they are established. Entities providing DNS services, TLD name registries, cloud computing services, data centre services, CDN services, managed services, managed security services, online marketplace, online search engine, or social networking platform shall fall under the jurisdiction of the Member State in which they have their main establishment in the Union. DNS providers, TLD registries, and domain registration entities shall fall under the jurisdiction of the Member State in which they are established.',
        "plain_english": "You are subject to NIS2 in the EU country where you are established — for certain digital services, it's where your main EU establishment is.",
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'primary_jurisdiction', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'jurisdiction', 'establishment'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Identify which EU member state has jurisdiction over your NIS2 obligations based on your main establishment.',
    },
    {
        "article": 'Article 27', "article_number": 27,
        "title": 'Register of entities',
        "chapter": 'Chapter IV — Jurisdiction and Registration', "category": 'Registration',
        "description": 'Member States shall establish a register of essential and important entities and entities providing domain name registration services. Entities shall submit to the competent authority at least the following information: name, address, registration number; sector and subsector; list of Member States where they provide services; contact details including email, phone; IP ranges; and date of submission. Entities shall update information without undue delay, and at least every two years.',
        "plain_english": 'You must register with your national NIS2 authority and keep your information up to date — including contact details, sector, and IP ranges.',
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'profile_field',
        "profile_field": 'nis2_data.nis2_registration_complete', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'registration', 'competent_authority'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.nis2_registration_complete == true'},
        "remediation_hint": 'Register with your national NIS2 competent authority. Update your registration at least every 2 years or when information changes.',
    },
    {
        "article": 'Article 28', "article_number": 28,
        "title": 'Database of domain name registration data',
        "chapter": 'Chapter IV — Jurisdiction and Registration', "category": 'Registration',
        "description": 'TLD name registries and entities providing domain name registration services shall collect and maintain accurate and complete domain name registration data in a dedicated database with due diligence in accordance with Union data protection law. The database shall contain information necessary to identify and contact the holders of the domain names and the points of contact administering the domain names.',
        "plain_english": 'Domain name registries and registrars must maintain accurate WHOIS-style databases with domain holder contact details.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'domain_registration', 'DNS', 'WHOIS'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Applies specifically to TLD registries and domain registrars — ensure accurate domain registration data is maintained.',
    },

    # Chapter V — Union Level Cybersecurity
    {
        "article": 'Article 29', "article_number": 29,
        "title": 'Cybersecurity information sharing arrangements',
        "chapter": 'Chapter V — Union Level Cybersecurity', "category": 'Information Sharing',
        "description": 'Member States shall ensure that essential and important entities and, where relevant, their suppliers or service providers, may exchange relevant cybersecurity information among themselves on a voluntary basis, including information relating to cyber threats, near misses, vulnerabilities, techniques and procedures, indicators of compromise, and cybersecurity tools. Such sharing shall be carried out through sharing arrangements with the aim of preventing, detecting, responding to, or recovering from incidents.',
        "plain_english": 'Organisations are encouraged to voluntarily share cyber threat intelligence and incident information with peers to improve collective defence.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": 'profile_field',
        "profile_field": 'nis2_data.participates_in_info_sharing', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'information_sharing', 'threat_intelligence'],
        "evaluation_logic": {'type': 'profile_field', 'check': 'nis2_data.participates_in_info_sharing == true'},
        "remediation_hint": 'Consider joining sector-specific Information Sharing and Analysis Centres (ISACs) or other threat intelligence sharing communities.',
    },
    {
        "article": 'Article 30', "article_number": 30,
        "title": 'Voluntary notification of relevant information',
        "chapter": 'Chapter V — Union Level Cybersecurity', "category": 'Information Sharing',
        "description": 'Member States shall ensure that entities that are not essential or important entities under NIS2 may voluntarily notify significant incidents, cyber threats and near misses to the competent authority or CSIRT. Voluntary notifications shall not result in the imposition of additional obligations on the notifying entity that would not have been imposed had it not submitted the notification.',
        "plain_english": "Even if NIS2 doesn't apply to you, you can voluntarily report cyber incidents and threats to national authorities without triggering additional obligations.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'voluntary_notification'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Consider voluntarily reporting significant cyber incidents even if outside NIS2 mandatory scope — it helps national threat intelligence.',
    },

    # Chapter VI — Supervisory and Enforcement
    {
        "article": 'Article 31', "article_number": 31,
        "title": 'General aspects of supervision and enforcement',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Enforcement',
        "description": 'Member States shall ensure competent authorities effectively supervise and take necessary measures to ensure compliance with NIS2. Competent authorities shall cooperate with each other, with the Commission, and with ENISA. Supervision shall be proportionate and risk-based. For essential entities, proactive supervision applies; for important entities, supervision is reactive (after indication of non-compliance).',
        "plain_english": "Essential entities face regular proactive audits and inspections; important entities are only investigated when there's evidence of non-compliance.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'nis2_data.entity_type', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'supervision', 'enforcement', 'essential_entity', 'important_entity'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Essential entities should prepare for proactive regulatory audits. Maintain audit-ready documentation of your cybersecurity measures.',
    },
    {
        "article": 'Article 32', "article_number": 32,
        "title": 'Supervisory and enforcement measures in relation to essential entities',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Enforcement',
        "description": 'For essential entities, competent authorities shall have powers to: conduct on-site inspections and remote supervision; carry out security audits; request information and documentation; issue warnings; issue binding instructions; require entities to implement security measures; require entities to inform users of threats; designate a monitoring officer; temporarily suspend or request judicial suspension of a service or activity; and impose administrative fines. Competent authorities may require essential entities to make a public declaration regarding non-compliance.',
        "plain_english": 'For essential entities, authorities can audit, inspect, issue binding instructions, suspend services, and impose fines up to €10M or 2% of global turnover.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'nis2_data.entity_type', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'enforcement', 'essential_entity', 'fines', 'suspension'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'If classified as essential, maintain comprehensive compliance documentation ready for proactive supervisory audits.',
    },
    {
        "article": 'Article 33', "article_number": 33,
        "title": 'Supervisory and enforcement measures in relation to important entities',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Enforcement',
        "description": 'For important entities, competent authorities shall have the same supervisory powers as for essential entities except that supervision is reactive rather than proactive. Important entities are subject to supervision only after receiving an indication of non-compliance, or on the basis of information, specific requests, notifications, or complaints. Fines for important entities: up to €7M or 1.4% of total worldwide annual turnover.',
        "plain_english": "Important entities are only investigated when there's a complaint or indication of non-compliance — fines up to €7M or 1.4% of global turnover.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'nis2_data.entity_type', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'enforcement', 'important_entity', 'fines'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": "Important entities should still implement all NIS2 measures — reactive supervision means you'll be investigated if something goes wrong.",
    },
    {
        "article": 'Article 34', "article_number": 34,
        "title": 'General conditions for imposing administrative fines on essential and important entities',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Fines',
        "description": 'Member States shall ensure that administrative fines for essential and important entities are effective, proportionate and dissuasive. Essential entities: maximum fine of at least €10,000,000 or 2% of total worldwide annual turnover, whichever is higher. Important entities: maximum fine of at least €7,000,000 or 1.4% of total worldwide annual turnover, whichever is higher. Management bodies of essential entities can be held personally liable and temporarily banned from management roles for repeated infringements.',
        "plain_english": 'NIS2 fines: essential entities up to €10M or 2% global turnover; important entities up to €7M or 1.4% global turnover. Management can be personally fined and banned.',
        "severity": Severity.CRITICAL, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": 'nis2_data.entity_type', "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'fines', 'penalties', 'management_liability'],
        "evaluation_logic": {'type': 'informational', 'essential_max': '€10M or 2% global turnover', 'important_max': '€7M or 1.4% global turnover'},
        "remediation_hint": 'Prioritise NIS2 compliance — fines and personal management liability make non-compliance extremely costly.',
    },
    {
        "article": 'Article 35', "article_number": 35,
        "title": 'Infringements involving a personal data breach',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Enforcement',
        "description": 'Where a NIS2 infringement also constitutes a personal data breach under GDPR, competent authorities and data protection authorities shall cooperate to ensure consistent enforcement. Fines under NIS2 and GDPR shall not be cumulative for the same conduct — the higher fine shall apply. Competent authorities shall inform data protection authorities where a NIS2 infringement results in a personal data breach.',
        "plain_english": "If a cyber incident is also a GDPR data breach, you won't be double-fined — only the higher of the NIS2 or GDPR fine applies.",
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'GDPR', 'personal_data_breach', 'double_fining'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Coordinate your NIS2 incident reporting and GDPR breach notification processes — a single incident may trigger both.',
    },
    {
        "article": 'Article 36', "article_number": 36,
        "title": 'Penalties',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Fines',
        "description": 'Member States shall lay down rules on penalties applicable to infringements of national measures adopted pursuant to this Directive and shall take all measures necessary to ensure that they are implemented. Penalties shall be effective, proportionate and dissuasive. Member States shall notify the Commission of those rules and of any subsequent amendment thereto without delay.',
        "plain_english": 'EU countries implement NIS2 penalties in national law — these must be effective, proportionate, and dissuasive.',
        "severity": Severity.HIGH, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'penalties', 'national_law'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": "Check your country's national NIS2 implementation law for specific penalty provisions beyond the EU minimums.",
    },
    {
        "article": 'Article 37', "article_number": 37,
        "title": 'Mutual assistance',
        "chapter": 'Chapter VI — Supervisory and Enforcement', "category": 'Enforcement',
        "description": 'At the request of a competent authority, other competent authorities may provide assistance with supervisory or enforcement actions concerning cross-border service providers. Requests for mutual assistance shall be proportionate. Requested authorities shall respond within one month and carry out the requested measures using their supervisory powers. Reasons must be given if assistance cannot be provided. Joint supervisory actions by two or more Member States, led by the competent authority of the Member State where the entity is established, are also part of this mutual assistance mechanism.',
        "plain_english": 'EU supervisory authorities assist each other in cross-border NIS2 enforcement cases.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'mutual_assistance', 'cross_border'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — relevant if subject to cross-border NIS2 supervision.',
    },

    # Chapter VII — Delegated and Implementing Acts
    {
        "article": 'Article 38', "article_number": 38,
        "title": 'Exercise of the delegation',
        "chapter": 'Chapter VII — Delegated and Implementing Acts', "category": 'Legislative',
        "description": 'The power to adopt delegated acts is conferred on the Commission for a period of five years from 17 January 2023. The European Parliament or the Council may revoke the delegation at any time.',
        "plain_english": 'The Commission can adopt supplementary NIS2 implementing rules for a renewable five-year period.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'joint_supervision', 'cross_border'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Cross-border organisations should prepare for coordinated multi-country regulatory inspections.',
    },
    {
        "article": 'Article 39', "article_number": 39,
        "title": 'Committee procedure',
        "chapter": 'Chapter VII — Delegated and Implementing Acts', "category": 'Legislative',
        "description": 'The Commission shall be assisted by a committee. Where reference is made to this Article, the examination procedure referred to in Article 5 of Regulation (EU) No 182/2011 shall apply.',
        "plain_english": 'The Commission uses a standard EU committee procedure when adopting NIS2 implementing measures.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'delegated_acts'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Monitor EU Official Journal for NIS2 delegated acts that may introduce new requirements.',
    },

    # Chapter VIII — Transitional and Final Provisions
    {
        "article": 'Article 40', "article_number": 40,
        "title": 'Review',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'By 17 October 2027 and every 36 months thereafter, the Commission shall review the functioning of this Directive and report to the European Parliament and the Council. The review shall assess whether the scope of this Directive should be extended, whether additional sectors or subsectors should be covered, and whether the supervisory framework is effective.',
        "plain_english": 'The Commission reviews NIS2 every 3 years from 2027 and may expand its scope to additional sectors.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'implementing_acts'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Informational — no direct action required for organisations.',
    },
    {
        "article": 'Article 41', "article_number": 41,
        "title": 'Transposition',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'Member States shall adopt and publish, by 17 October 2024, the measures necessary to comply with this Directive. Member States shall apply those measures from 18 October 2024. Member States shall communicate to the Commission the text of the measures of national law which they adopt in the field covered by this Directive.',
        "plain_english": 'EU countries had to implement NIS2 into national law by 17 October 2024, with application from 18 October 2024.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'review', 'legislative'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Monitor NIS2 review outcomes — additional sectors may come into scope from 2027 onwards.',
    },
    {
        "article": 'Article 42', "article_number": 42,
        "title": 'Amendments to Regulation (EU) No 910/2014',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'Regulation (EU) No 910/2014 (eIDAS) is amended to align trust service providers with NIS2 security requirements. Trust service providers are subject to NIS2 obligations for cybersecurity risk management and incident reporting.',
        "plain_english": 'NIS2 aligns the eIDAS Regulation (electronic signatures and trust services) with NIS2 cybersecurity requirements.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'eIDAS', 'trust_services'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'If you are an eIDAS trust service provider, ensure compliance with both eIDAS and NIS2 cybersecurity requirements.',
    },
    {
        "article": 'Article 43', "article_number": 43,
        "title": 'Amendments to Directive (EU) 2018/1972',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'Directive (EU) 2018/1972 (European Electronic Communications Code) is amended to align providers of public electronic communications networks and services with NIS2 security and incident reporting obligations.',
        "plain_english": 'NIS2 aligns telecom provider cybersecurity obligations with the NIS2 framework.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": False, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'telecoms', 'electronic_communications'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Applies to electronic communications providers — align cybersecurity obligations under both NIS2 and the EECC.',
    },
    {
        "article": 'Article 44', "article_number": 44,
        "title": 'Repeal',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'Directive (EU) 2016/1148 (NIS1) is repealed with effect from 18 October 2024. References to the repealed Directive shall be construed as references to this Directive.',
        "plain_english": 'NIS1 (the original 2016 cybersecurity directive) was replaced by NIS2 on 18 October 2024.',
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'NIS1', 'repeal'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'Ensure all internal policies reference NIS2 (2022/2555) and not the old NIS1 directive.',
    },
    {
        "article": 'Article 45', "article_number": 45,
        "title": 'Entry into force',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'This Directive shall enter into force on the twentieth day following that of its publication in the Official Journal of the European Union. It was published on 27 December 2022 and entered into force on 16 January 2023. Member States were required to transpose it by 17 October 2024.',
        "plain_english": 'NIS2 entered into force on 16 January 2023 and became applicable in member states from 18 October 2024.',
        "severity": Severity.MEDIUM, "fine_tier": None, "is_mandatory": True, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'transposition', 'national_law'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": "Check your country's national NIS2 implementation law — requirements may go beyond the EU minimum.",
    },
    {
        "article": 'Article 46', "article_number": 46,
        "title": 'Addressees',
        "chapter": 'Chapter VIII — Transitional and Final Provisions', "category": 'Legislative',
        "description": 'This Directive is addressed to the Member States.',
        "plain_english": "NIS2 is a directive aimed at EU governments, who are responsible for writing it into their own national laws. It doesn't directly bind your organisation, your country's implementing law does.",
        "severity": Severity.LOW, "fine_tier": None, "is_mandatory": False, "check_type": 'informational',
        "profile_field": None, "applies_to_b2c": True, "applies_to_b2b": True,
        "applicability_tags": ['NIS2', 'addressees', 'legislative'],
        "evaluation_logic": {'type': 'informational'},
        "remediation_hint": 'NIS2 has been fully applicable since 18 October 2024 — ensure compliance now.',
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
