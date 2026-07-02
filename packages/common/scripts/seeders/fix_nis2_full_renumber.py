"""
NIS2 full renumber + content correction — 46-row one-off DB fix.

Applies, against the already-seeded NIS2 rows:
  1. Two net-new rows (real Art 5 "Minimum harmonisation", real Art 6 "Definitions")
  2. A 12-row renumber cascade (DB5->7, DB6->12, DB7->9, DB9->10, DB10->11,
     DB12->16, DB14->15, DB15->14, DB16->17, DB17->19, plus the merge-source
     DB11 and the delete-source DB19, both staged then removed) via two-pass
     negative-staging to avoid any transient collisions
  3. A vulnerability-disclosure merge (old DB6 -> new article_number=12,
     absorbing old DB11's security-researcher clause; old DB11 deleted)
  4. Content-only fixes at article_number 13, 18, 24, 25 (no renumber)
  5. A 9-row back-block cascade at article_number 38-46 (pure content moves,
     article_number values never change) plus new "Addressees" content at 46

See docs/nis2_content_corrections.md and docs/nis2_full_renumber_map.md for
the full rationale and source-text citations.

Transaction strategy: Pass 1 (negative staging) is flushed but not committed,
then Pass 2 (final values + content fixes + back-block + inserts + delete) is
applied and the whole thing commits once at the end. The unique constraint on
rules is (regulation_id, article) — the string column, not article_number —
so it is never actually at risk of mid-transaction collision here; the
negative staging is done anyway per the approved plan, purely to keep
article_number unique at every intermediate step as a safety property
independent of what the DB constraint technically enforces.

Run inside Docker:
  docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway \
    uv run python /app/packages/common/scripts/seeders/fix_nis2_full_renumber.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from common.config import BaseServiceSettings
from common.models.regulation import Regulation
from common.models.rule import Rule, Severity
from common.utils.ids import generate_rule_id

settings = BaseServiceSettings()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Pass-1 staging: old article_number -> temporary negative value.
# Includes every row whose article_number changes, plus the two delete-source
# rows (11, 19) which must vacate their slots before other rows move in.
STAGE_MAP = {
    5: -5, 6: -6, 7: -7, 9: -9, 10: -10, 11: -11,
    12: -12, 14: -14, 15: -15, 16: -16, 17: -17, 19: -19,
}

# Pass-2 final moves: temporary negative value -> final article_number.
# DB11 and DB19 are intentionally absent here — they are deleted, not moved.
FINAL_MAP = {
    -5: 7,    # DB5  -> real Art 7  (National cybersecurity strategy)
    -6: 12,   # DB6  -> real Art 12 (Coordinated vulnerability disclosure, merged)
    -7: 9,    # DB7  -> real Art 9  (National cyber crisis management framework)
    -9: 10,   # DB9  -> real Art 10 (CSIRTs)
    -10: 11,  # DB10 -> real Art 11 (Requirements for CSIRTs)
    -12: 16,  # DB12 -> real Art 16 (Cyber crisis management / EU-CyCLONe)
    -14: 15,  # DB14 -> real Art 15 (CSIRTs network)
    -15: 14,  # DB15 -> real Art 14 (NIS Cooperation Group)
    -16: 17,  # DB16 -> real Art 17 (International cooperation)
    -17: 19,  # DB17 -> real Art 19 (Peer reviews)
}

NEW_ART_5 = dict(
    article="Article 5", article_number=5,
    title="Minimum harmonisation",
    chapter="Chapter I — General Provisions", category="General",
    description=(
        "This Directive does not prevent Member States from adopting or "
        "maintaining provisions ensuring a higher level of cybersecurity, "
        "provided that such provisions are consistent with Member States' "
        "obligations under Union law."
    ),
    plain_english=(
        "EU countries can set stricter cybersecurity rules than NIS2's "
        "minimum, as long as those stricter rules still comply with other "
        "EU law."
    ),
    severity=Severity.LOW, fine_tier=None, is_mandatory=False, check_type="informational",
    profile_field=None, applies_to_b2c=True, applies_to_b2b=True,
    applicability_tags=["NIS2", "minimum_harmonisation", "general"],
    evaluation_logic={"type": "informational"},
    remediation_hint="Informational — no direct action required for organisations.",
)

NEW_ART_6 = dict(
    article="Article 6", article_number=6,
    title="Definitions",
    chapter="Chapter I — General Provisions", category="General",
    description=(
        'For the purposes of this Directive, the following definitions apply: '
        '"network and information system" means an electronic communications '
        "network, any device or group of interconnected devices which carry "
        "out automatic processing of digital data, or digital data stored, "
        "processed, retrieved, or transmitted by the above elements for the "
        "purpose of their operation, use, protection, and maintenance; "
        '"security of network and information systems" means the ability of '
        "network and information systems to resist, at a given level of "
        "confidence, any event that may compromise the availability, "
        "authenticity, integrity, or confidentiality of stored, transmitted, "
        'or processed data or of the related services; "national '
        'cybersecurity strategy" means a coherent framework of a Member State '
        "providing strategic objectives and priorities in the area of "
        'cybersecurity and the governance to achieve them; "near miss" means '
        "an event that could have compromised the availability, authenticity, "
        "integrity, or confidentiality of stored, transmitted, or processed "
        "data or of the services offered by, or accessible via, network and "
        "information systems, but that was successfully prevented from "
        'materialising or that did not materialise; "incident" means an '
        "event compromising the availability, authenticity, integrity, or "
        "confidentiality of stored, transmitted, or processed data or of the "
        "services offered by, or accessible via, network and information "
        'systems; "large-scale cybersecurity incident" means an incident '
        "which causes a level of disruption that exceeds a Member State's "
        "capacity to respond to it or which has a significant impact on at "
        'least two Member States; "incident handling" means any actions and '
        "procedures aiming to prevent, detect, analyse, and contain or to "
        'respond to and recover from an incident; "risk" means the potential '
        "for loss or disruption caused by an incident, expressed as a "
        "combination of the magnitude of such loss or disruption and the "
        'likelihood of occurrence of the incident; "cyber threat" has the '
        "meaning given in Article 2, point (8), of Regulation (EU) 2019/881; "
        '"significant cyber threat" means a cyber threat which, based on its '
        "technical characteristics, can be assumed to have the potential to "
        "have a severe impact on the network and information systems of an "
        "entity or the users of the entity's services by causing considerable "
        'material or non-material damage; "ICT product", "ICT service", and '
        '"ICT process" have the meanings given in Article 2, points (12), '
        '(13), and (14), of Regulation (EU) 2019/881; "vulnerability" means a '
        "weakness, susceptibility, or flaw of ICT products or ICT services "
        "that can be exploited by a cyber threat; further definitions cover "
        "standard, technical specification, internet exchange point, domain "
        "name system (DNS), DNS service provider, top-level domain name "
        "registry, entity providing domain name registration services, "
        "digital service, trust service and qualified trust service (by "
        "reference to Regulation (EU) No 910/2014), online marketplace, "
        "online search engine, cloud computing service, data centre service, "
        "content delivery network, social networking services platform, "
        "representative, public administration entity, public electronic "
        "communications network and electronic communications service (by "
        "reference to Directive (EU) 2018/1972), entity, managed service "
        "provider, managed security service provider, and research "
        "organisation."
    ),
    plain_english=(
        "This article defines the key terms used throughout NIS2, including "
        "incident, near miss, cyber threat, vulnerability, and the different "
        "categories of digital infrastructure and service providers the law "
        "applies to."
    ),
    severity=Severity.LOW, fine_tier=None, is_mandatory=False, check_type="informational",
    profile_field=None, applies_to_b2c=True, applies_to_b2b=True,
    applicability_tags=["NIS2", "definitions", "general"],
    evaluation_logic={"type": "informational"},
    remediation_hint="Informational — no direct action required for organisations.",
)

CONTENT_FIXES = {
    13: dict(
        title="Cooperation at national level",
        chapter="Chapter III — Cybersecurity Risk Management and Reporting", category="Cooperation",
        description=(
            "Where the competent authority or authorities, the single point "
            "of contact, and the CSIRT or CSIRTs of a Member State are "
            "separate entities, they shall cooperate with each other "
            "regarding the fulfilment of the obligations laid down in this "
            "Directive. Member States shall ensure that either their "
            "competent authorities or their CSIRTs receive notifications of "
            "significant incidents (Article 23) and of incidents, cyber "
            "threats, and near misses (Article 30). Member States shall "
            "ensure that their CSIRTs or, where applicable, their competent "
            "authorities inform their single points of contact about "
            "notifications of incidents, cyber threats, and near misses "
            "submitted pursuant to this Directive. In order for the "
            "obligations of the competent authorities, single points of "
            "contact, and CSIRTs to be fulfilled effectively, Member States "
            "shall ensure, to the extent possible, appropriate cooperation "
            "between those bodies and law enforcement authorities, data "
            "protection authorities, the national authorities under "
            "Regulation (EC) No 300/2008 and Regulation (EU) 2018/1139, the "
            "authorities responsible under the Digital Operational "
            "Resilience Act (Regulation (EU) 2022/2554), the national "
            "regulatory authorities under Directive (EU) 2018/1972, and the "
            "competent authorities under the Critical Entities Resilience "
            "Directive (EU) 2022/2557, within that Member State."
        ),
        plain_english=(
            "Within each EU country, the cybersecurity authority, the single "
            "point of contact, and the national CSIRT must coordinate with "
            "each other and with related authorities like data protection "
            "regulators and law enforcement when handling NIS2 obligations."
        ),
    ),
    18: dict(
        title="Report on the state of cybersecurity in the Union",
        chapter="Chapter III — Cybersecurity Risk Management and Reporting", category="Reporting",
        description=(
            "ENISA shall, in cooperation with the Commission and the "
            "Cooperation Group, adopt a biennial report on the state of "
            "cybersecurity in the Union and submit that report to the "
            "European Parliament. The report shall, among other things, be "
            "made available in a machine-readable format and shall include: "
            "(a) an assessment of the development of cybersecurity "
            "capabilities across the Union; (b) an assessment of the level "
            "of cybersecurity awareness and cyber hygiene among citizens and "
            "entities, including small and medium enterprises; (c) an "
            "aggregated assessment of the results of peer reviews referred "
            "to in Article 19; (d) an aggregated assessment of the level of "
            "maturity of cybersecurity capabilities and resources across the "
            "Union, including at sector level, and of the extent to which "
            "national cybersecurity strategies are aligned. The report shall "
            "include specific policy recommendations to address shortcomings "
            "and raise the level of cybersecurity across the Union, and a "
            "summary of the findings from ENISA's biennial technical EU "
            "cybersecurity situation reports on incidents and cyber threats. "
            "ENISA shall develop the methodology, including relevant "
            "variables (quantitative and qualitative indicators), for the "
            "assessment referred to above, in cooperation with the "
            "Commission, the Cooperation Group, and the CSIRTs network."
        ),
        plain_english=(
            "Every two years, ENISA publishes a report on the overall state "
            "of cybersecurity across the EU, covering capability levels, "
            "public awareness, and policy recommendations. This is a "
            "government/EU-level reporting obligation, not something your "
            "organisation needs to act on directly."
        ),
        profile_field=None,
        evaluation_logic={"type": "informational"},
        is_mandatory=False,
        check_type="informational",
        severity=Severity.LOW,
        applicability_tags=["NIS2", "ENISA", "biennial_report", "cybersecurity_state"],
    ),
    24: dict(
        title="Use of European cybersecurity certification schemes",
        chapter="Chapter III — Cybersecurity Risk Management and Reporting", category="Certification",
        description=(
            "Member States may require essential and important entities to "
            "use particular ICT products, ICT services, and ICT processes, "
            "developed by the essential or important entity or procured "
            "from third parties, that are certified under European "
            "cybersecurity certification schemes adopted pursuant to "
            "Article 49 of Regulation (EU) 2019/881, in order to demonstrate "
            "compliance with the cybersecurity risk-management requirements "
            "under Article 21. Member States shall also encourage essential "
            "and important entities to use qualified trust services. The "
            "Commission is empowered to adopt delegated acts, in accordance "
            "with Article 38, to supplement this Directive by specifying "
            "which categories of essential and important entities shall be "
            "required to use certain certified ICT products, ICT services, "
            "and ICT processes or to obtain a certificate under a European "
            "cybersecurity certification scheme adopted pursuant to Article "
            "49 of Regulation (EU) 2019/881. Such delegated acts shall be "
            "adopted where an insufficient level of cybersecurity has been "
            "identified, and shall include an implementation period. Before "
            "adopting such delegated acts, the Commission shall carry out an "
            "impact assessment and conduct consultations in accordance with "
            "Article 56 of Regulation (EU) 2019/881. Where no appropriate "
            "European cybersecurity certification scheme is available for "
            "the purposes referred to above, the Commission may, after "
            "consulting the Cooperation Group and the European "
            "Cybersecurity Certification Group, request ENISA to prepare a "
            "possible scheme pursuant to Article 48(2) of Regulation (EU) "
            "2019/881."
        ),
        plain_english=(
            "EU countries can require organisations to use cybersecurity-"
            "certified ICT products and services to prove they meet NIS2's "
            "risk-management standards. The EU can also make specific "
            "certifications mandatory for certain types of organisations if "
            "security gaps are found."
        ),
        profile_field=None,
        is_mandatory=False,
        check_type="informational",
        severity=Severity.MEDIUM,
        applicability_tags=["NIS2", "certification", "EU_Cybersecurity_Act", "delegated_acts"],
    ),
    25: dict(
        title="Standardisation",
        chapter="Chapter III — Cybersecurity Risk Management and Reporting", category="Standardisation",
        description=(
            "In order to promote the convergent implementation of Article "
            "21(1) and (2), Member States shall, without imposing or "
            "discriminating in favour of the use of a particular type of "
            "technology, encourage the use of European and international "
            "standards and technical specifications relevant to the "
            "security of network and information systems. ENISA, in "
            "cooperation with Member States, shall draw up advice and "
            "guidelines regarding the technical areas to be considered in "
            "relation to the first paragraph, as well as regarding already "
            "existing standards, including Member States' national "
            "standards, which would allow for those areas to be covered."
        ),
        plain_english=(
            "EU countries encourage (without mandating any specific vendor "
            "or technology) the use of recognised European and "
            "international cybersecurity standards, like ISO 27001, to help "
            "organisations meet NIS2's security requirements consistently."
        ),
        profile_field=None,
        evaluation_logic={"type": "informational"},
        is_mandatory=False,
        check_type="informational",
        severity=Severity.LOW,
        applicability_tags=["NIS2", "standardisation", "ENISA", "ISO_27001"],
    ),
}

ART_37_APPEND = (
    " Joint supervisory actions by two or more Member States, led by the "
    "competent authority of the Member State where the entity is "
    "established, are also part of this mutual assistance mechanism."
)

NEW_ART_46 = dict(
    title="Addressees",
    chapter="Chapter VIII — Transitional and Final Provisions", category="Legislative",
    description="This Directive is addressed to the Member States.",
    plain_english=(
        "NIS2 is a directive aimed at EU governments, who are responsible "
        "for writing it into their own national laws. It doesn't directly "
        "bind your organisation, your country's implementing law does."
    ),
    severity=Severity.LOW, fine_tier=None, is_mandatory=False, check_type="informational",
    profile_field=None, applicability_tags=["NIS2", "addressees", "legislative"],
)


async def fix() -> None:
    async with SessionLocal() as session:
        reg = await session.scalar(select(Regulation).where(Regulation.name == "NIS2"))
        if not reg:
            print("NIS2 not seeded — nothing to fix.")
            return

        async def get(article_number: int) -> Rule | None:
            return await session.scalar(
                select(Rule).where(Rule.regulation_id == reg.id, Rule.article_number == article_number)
            )

        # ── Pass 1: stage all touched rows to temporary negative values ────
        rows_by_old_number: dict[int, Rule] = {}
        for old_num in STAGE_MAP:
            rule = await get(old_num)
            if rule is None:
                raise RuntimeError(f"Expected existing NIS2 row at article_number={old_num}, found none.")
            rows_by_old_number[old_num] = rule
            rule.article_number = STAGE_MAP[old_num]
            rule.article = f"Article TEMP{STAGE_MAP[old_num]}"
        await session.flush()
        print("✓ Pass 1 staged 12 rows to temporary negative article_number values.")

        # ── Pass 2a: resolve staged rows to final article_number values ────
        for temp_num, final_num in FINAL_MAP.items():
            rule = next(r for old, r in rows_by_old_number.items() if STAGE_MAP[old] == temp_num)
            rule.article_number = final_num
            rule.article = f"Article {final_num}"
        await session.flush()
        print("✓ Pass 2 resolved 10 staged rows to final article_number values.")

        # ── Art 12 merge: DB6 (now at 12) absorbs DB11's researcher clause ─
        db6_now_12 = rows_by_old_number[6]
        db11_row = rows_by_old_number[11]
        db6_now_12.title = "Coordinated vulnerability disclosure and a European vulnerability database"
        db6_now_12.description = (
            db6_now_12.description.rstrip(".")
            + ". To support this process, Member States shall also take the "
            "necessary measures to allow security researchers to report "
            "vulnerabilities they have discovered under legal protection, "
            "with CSIRTs acting as trusted intermediaries between reporting "
            "researchers and the manufacturers or providers of the affected "
            "ICT products or services."
        )
        db6_now_12.plain_english = (
            "EU countries must have a coordinated vulnerability disclosure "
            "process, including a European vulnerability database "
            "maintained by ENISA, and must legally protect security "
            "researchers who responsibly report vulnerabilities they find."
        )
        db6_now_12.applicability_tags = ["NIS2", "vulnerability_disclosure", "ENISA", "security_researchers"]
        print("✓ Merged DB11's researcher-protection clause into DB6 (now article_number=12).")

        # ── Deletes: old DB11 (merged away) and old DB19 (superseded by 24) ─
        db19_row = rows_by_old_number[19]
        await session.delete(db11_row)
        await session.delete(db19_row)
        print("✓ Deleted old DB11 (merged into 12) and old DB19 (superseded by corrected 24).")

        # ── Content-only fixes: 13, 18, 24, 25 ──────────────────────────────
        for article_number, fields in CONTENT_FIXES.items():
            rule = await get(article_number)
            if rule is None:
                raise RuntimeError(f"Expected existing NIS2 row at article_number={article_number} for content fix.")
            for field, value in fields.items():
                setattr(rule, field, value)
            print(f"✓ Applied content fix to article_number={article_number}.")

        # ── Net-new inserts: Article 5, Article 6 ───────────────────────────
        session.add(Rule(rule_id=generate_rule_id(), regulation_id=reg.id, **NEW_ART_5))
        session.add(Rule(rule_id=generate_rule_id(), regulation_id=reg.id, **NEW_ART_6))
        print("✓ Inserted new Article 5 (Minimum harmonisation) and Article 6 (Definitions).")

        # ── Back block: read current text for 39,40,41,45,46 BEFORE writing ─
        rule_38 = await get(38)
        rule_39 = await get(39)
        rule_40 = await get(40)
        rule_41 = await get(41)
        rule_45 = await get(45)
        rule_46 = await get(46)
        for r, num in ((rule_38, 38), (rule_39, 39), (rule_40, 40), (rule_41, 41), (rule_45, 45), (rule_46, 46)):
            if r is None:
                raise RuntimeError(f"Expected existing NIS2 row at article_number={num} for back-block cascade.")

        src_39 = dict(title=rule_39.title, description=rule_39.description, plain_english=rule_39.plain_english, chapter=rule_39.chapter, category=rule_39.category)
        src_40 = dict(title=rule_40.title, description=rule_40.description, plain_english=rule_40.plain_english, chapter=rule_40.chapter, category=rule_40.category)
        src_41 = dict(title=rule_41.title, description=rule_41.description, plain_english=rule_41.plain_english, chapter=rule_41.chapter, category=rule_41.category)
        src_45 = dict(title=rule_45.title, description=rule_45.description, plain_english=rule_45.plain_english, chapter=rule_45.chapter, category=rule_45.category)
        src_46 = dict(title=rule_46.title, description=rule_46.description, plain_english=rule_46.plain_english, chapter=rule_46.chapter, category=rule_46.category)

        # 37: append joint-supervisory-actions sentence
        rule_37 = await get(37)
        if rule_37 is None:
            raise RuntimeError("Expected existing NIS2 row at article_number=37.")
        rule_37.description = rule_37.description.rstrip(".") + "." + ART_37_APPEND

        # 38 <- old 39 content
        for field, value in src_39.items():
            setattr(rule_38, field, value)
        # 39 <- old 40 content
        for field, value in src_40.items():
            setattr(rule_39, field, value)
        # 40 <- old 41 content
        for field, value in src_41.items():
            setattr(rule_40, field, value)
        # 41 <- old 45 content
        for field, value in src_45.items():
            setattr(rule_41, field, value)
        # 42, 43, 44: no change
        # 45 <- old 46 content
        for field, value in src_46.items():
            setattr(rule_45, field, value)
        # 46 <- new Addressees content
        for field, value in NEW_ART_46.items():
            setattr(rule_46, field, value)
        print("✓ Applied back-block cascade (37 append, 38<-39, 39<-40, 40<-41, 41<-45, 45<-46, 46<-new Addressees).")

        await session.commit()
        print("✅ NIS2 full renumber + content fix complete.")


if __name__ == "__main__":
    asyncio.run(fix())
