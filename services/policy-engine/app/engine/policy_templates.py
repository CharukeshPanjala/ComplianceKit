# WHAT: Policy section templates | CHANGE: new file | WHY: COM-175 — mandatory sections per EU policy type (Art. 13/14, 28, 33/34, NIS2, AI Act Art. 9/13), used for AI prompts and stub fallback

from common.models.policy import PolicyType

POLICY_LABELS: dict[PolicyType, str] = {
    PolicyType.PRIVACY_NOTICE: "Privacy Notice",
    PolicyType.DPA: "Data Processing Agreement",
    PolicyType.COOKIE_POLICY: "Cookie Policy",
    PolicyType.DATA_RETENTION: "Data Retention Policy",
    PolicyType.INCIDENT_RESPONSE: "Incident Response Policy",
    PolicyType.AI_GOVERNANCE: "AI Governance Policy",
    PolicyType.ROPA: "Records of Processing Activities",
    PolicyType.OTHER: "Compliance Policy",
}

# policy_type -> [(section title, what it must contain)]
POLICY_SECTIONS: dict[PolicyType, list[tuple[str, str]]] = {
    PolicyType.PRIVACY_NOTICE: [
        ("Who We Are", "Identity and contact details of the data controller, and EU representative if applicable"),
        ("Data Protection Officer", "Name and contact details of the DPO, or contact point for data protection queries"),
        ("What Data We Collect", "Categories of personal data processed"),
        ("Why We Process Your Data", "Purposes of processing and the legal basis under Art. 6 for each purpose"),
        ("Legitimate Interests", "Where the legal basis is legitimate interests, explain the specific interest pursued"),
        ("Who We Share Your Data With", "Recipients or categories of recipients of personal data"),
        ("International Transfers", "Whether data is transferred outside the EEA and the safeguard relied on"),
        ("How Long We Keep Your Data", "Retention period or the criteria used to determine it"),
        ("Your Rights", "Right of access, rectification, erasure, restriction, portability, objection"),
        ("Withdrawing Consent", "How to withdraw consent where processing is based on consent"),
        ("Automated Decision-Making", "Whether automated decision-making or profiling takes place and its logic and consequences"),
        ("How to Complain", "Right to lodge a complaint with a supervisory authority"),
    ],
    PolicyType.DPA: [
        ("Subject Matter and Duration", "Subject matter, duration, nature and purpose of the processing"),
        ("Categories of Data and Data Subjects", "Types of personal data and categories of data subjects"),
        ("Processing on Instructions", "The processor processes personal data only on documented instructions from the controller"),
        ("Confidentiality", "Persons authorised to process the data are bound by confidentiality"),
        ("Security Measures", "Technical and organisational measures implemented per Art. 32"),
        ("Sub-processors", "Conditions for engaging sub-processors and notification of changes"),
        ("Assistance with Data Subject Rights", "Processor assists the controller in responding to Art. 15-22 requests"),
        ("Assistance with Compliance", "Processor assists with breach notification, DPIAs and prior consultation under Art. 32-36"),
        ("Deletion or Return of Data", "Personal data is deleted or returned at the end of the contract"),
        ("Audit Rights", "The controller's right to audit and inspect the processor's compliance"),
        ("International Transfers", "Safeguards for transfers outside the EEA, including Standard Contractual Clauses where relevant"),
    ],
    PolicyType.COOKIE_POLICY: [
        ("What Are Cookies", "Brief explanation of cookies and similar tracking technologies"),
        ("Types of Cookies We Use", "Categories: strictly necessary, performance, functional, marketing"),
        ("Cookies in Detail", "Table of individual cookies with name, purpose, duration and provider"),
        ("Third-Party Cookies", "Third parties that set cookies and what data is shared with them"),
        ("Your Consent", "How consent is obtained, the option to refuse, and granular consent per category"),
        ("Managing Cookies", "How users can manage, block or delete cookies via browser settings"),
        ("Changes to This Policy", "How updates to the cookie policy are communicated"),
    ],
    PolicyType.DATA_RETENTION: [
        ("Purpose", "Why this policy exists and its relation to the storage limitation principle (Art. 5(1)(e))"),
        ("Scope", "Which systems, data categories and processing activities this policy covers"),
        ("Retention Schedule", "Table of data categories, processing purpose, and retention period for each"),
        ("Determining Retention Periods", "Criteria used where a fixed period cannot be set"),
        ("Deletion and Anonymisation", "Procedures for securely deleting or anonymising data at the end of retention"),
        ("Roles and Responsibilities", "Who owns and enforces the retention schedule"),
        ("Periodic Review", "How often the retention schedule is reviewed and updated"),
        ("Exceptions", "Legal holds, archiving in the public interest, research and statistical retention"),
    ],
    PolicyType.INCIDENT_RESPONSE: [
        ("Purpose and Scope", "Objective of the policy and the systems and data it covers"),
        ("Incident Classification", "Severity levels and types of security incidents"),
        ("Detection and Internal Reporting", "How incidents are detected and reported internally"),
        ("Escalation and Communication Plan", "Internal escalation path and stakeholder communication"),
        ("Containment and Recovery", "Steps to contain, eradicate and recover from an incident"),
        ("Notifying the Supervisory Authority", "GDPR Art. 33 72-hour notification, and NIS2 24-hour early warning, 72-hour report and 30-day final report where applicable"),
        ("Notifying Affected Individuals", "When and how data subjects are notified per Art. 34"),
        ("Post-Incident Review", "Documentation, lessons learned and follow-up actions"),
    ],
    PolicyType.AI_GOVERNANCE: [
        ("Purpose and Scope", "Which AI systems this policy governs and its objectives"),
        ("AI System Inventory and Risk Classification", "Register of AI systems and their risk category under the EU AI Act"),
        ("Risk Management System", "Continuous risk identification, assessment and mitigation per Art. 9"),
        ("Human Oversight", "Measures enabling human review and intervention in AI-driven decisions"),
        ("Technical Documentation", "Records kept on system design, training data and performance"),
        ("Training Data Governance", "How training and validation data is sourced, checked and documented"),
        ("Transparency to Users and Deployers", "Information provided per Art. 13: purpose, limitations, accuracy, oversight"),
        ("Post-Market Monitoring", "Ongoing monitoring for emerging risks and incident reporting"),
        ("Roles and Responsibilities", "Who is accountable for AI governance within the organisation"),
    ],
}

GENERIC_SECTIONS: list[tuple[str, str]] = [
    ("Purpose", "Why this policy exists"),
    ("Scope", "What this policy covers"),
    ("Policy Statement", "The core commitments and procedures"),
    ("Roles and Responsibilities", "Who is accountable"),
    ("Review", "How and when this policy is reviewed"),
]


def get_sections(policy_type: PolicyType) -> list[tuple[str, str]]:
    return POLICY_SECTIONS.get(policy_type, GENERIC_SECTIONS)
