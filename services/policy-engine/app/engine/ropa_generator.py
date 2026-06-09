# WHAT: ROPA generator engine | CHANGE: new file | WHY: COM-172 — auto-build draft RopaEntry objects from company profile
import uuid
from dataclasses import dataclass

from common.models.ropa import (
    RopaEntry,
    RopaDataRole,
    RopaLegalBasis,
    RopaSource,
    RopaStatus,
    SpecialCategoryCondition,
    TransferMechanism,
)


# ── Constants ─────────────────────────────────────────────────────────────────

SPECIAL_CATEGORIES = {
    "health", "biometric", "genetic", "racial_ethnic",
    "political", "religious", "trade_union", "sexual_orientation",
    "criminal_convictions",
}

# purpose slug → (activity_name, category, default legal basis)
ACTIVITY_MAP: dict[str, tuple[str, str, RopaLegalBasis]] = {
    "marketing":              ("Marketing and Communications",              "marketing",         RopaLegalBasis.CONSENT),
    "customer_management":    ("Customer Data Management",                  "customer",          RopaLegalBasis.CONTRACT),
    "analytics":              ("Website and Product Analytics",             "analytics",         RopaLegalBasis.LEGITIMATE_INTERESTS),
    "hr_management":          ("Employee and HR Data Processing",           "hr",                RopaLegalBasis.CONTRACT),
    "user_authentication":    ("User Authentication and Account Management","authentication",    RopaLegalBasis.CONTRACT),
    "payment_processing":     ("Payment Processing",                        "finance",           RopaLegalBasis.CONTRACT),
    "fraud_prevention":       ("Fraud Prevention and Security",             "security",          RopaLegalBasis.LEGITIMATE_INTERESTS),
    "legal_compliance":       ("Legal and Regulatory Compliance",           "legal",             RopaLegalBasis.LEGAL_OBLIGATION),
    "customer_support":       ("Customer Support and Communication",        "support",           RopaLegalBasis.CONTRACT),
    "product_improvement":    ("Product Development and Improvement",       "product",           RopaLegalBasis.LEGITIMATE_INTERESTS),
    "research":               ("Research and Development",                  "research",          RopaLegalBasis.LEGITIMATE_INTERESTS),
    "recruitment":            ("Recruitment and Talent Acquisition",        "hr",                RopaLegalBasis.LEGITIMATE_INTERESTS),
    "contract_management":    ("Contract and Supplier Management",          "legal",             RopaLegalBasis.CONTRACT),
    "security_monitoring":    ("Security and Access Monitoring",            "security",          RopaLegalBasis.LEGITIMATE_INTERESTS),
}

LAWFUL_BASIS_MAP: dict[str, RopaLegalBasis] = {
    "consent":               RopaLegalBasis.CONSENT,
    "contract":              RopaLegalBasis.CONTRACT,
    "legal_obligation":      RopaLegalBasis.LEGAL_OBLIGATION,
    "vital_interests":       RopaLegalBasis.VITAL_INTERESTS,
    "public_task":           RopaLegalBasis.PUBLIC_TASK,
    "legitimate_interests":  RopaLegalBasis.LEGITIMATE_INTERESTS,
}


# ── Result dataclass (unsaved) ────────────────────────────────────────────────

@dataclass
class GeneratedEntry:
    activity_name: str
    purpose: str
    category: str
    legal_basis: RopaLegalBasis
    data_role: RopaDataRole
    data_categories: list[str]
    data_subject_categories: list[str]
    has_special_category_data: bool
    special_category_types: list[str]
    special_category_condition: SpecialCategoryCondition | None
    has_automated_decision_making: bool
    processing_locations: list[str]
    third_party_transfers: dict | None
    transfer_mechanism: TransferMechanism | None
    processors: dict | None
    requires_dpia: bool
    security_measures: str | None


# ── Engine ────────────────────────────────────────────────────────────────────

class RopaGenerator:

    def __init__(self, profile: dict):
        self.profile = profile
        self.gdpr = profile.get("gdpr_data") or {}
        self.ai = profile.get("ai_act_data") or {}

        self.data_categories: list[str] = profile.get("data_categories_processed") or []
        self.data_subject_categories: list[str] = profile.get("data_subject_categories") or []
        self.processing_purposes: list[str] = profile.get("processing_purposes") or []
        self.tech_stack: list[str] = profile.get("tech_stack") or []
        self.cloud_providers: list[str] | dict = profile.get("cloud_providers") or []
        self.uses_cloud: bool = profile.get("uses_cloud_services") or False
        self.jurisdiction: str = profile.get("primary_jurisdiction") or ""
        self.company_size: str = profile.get("company_size") or ""
        self.number_of_subjects: str = profile.get("number_of_data_subjects") or ""

        raw_role = (profile.get("data_role") or "controller").lower()
        self.data_role = RopaDataRole.PROCESSOR if raw_role == "processor" else RopaDataRole.CONTROLLER

        self._special_types = [c for c in self.data_categories if c in SPECIAL_CATEGORIES]
        self._has_special = len(self._special_types) > 0
        self._transfers_outside_eea: bool = self.gdpr.get("transfers_outside_eea", False)
        self._uses_processors: bool = self.gdpr.get("uses_data_processors", False)
        self._lawful_bases: list[str] = self.gdpr.get("lawful_bases") or []
        self._has_automated_decisions: bool = self.ai.get("uses_ai", False)

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self) -> list[GeneratedEntry]:
        purposes = self.processing_purposes or ["data_processing"]
        return [self._build_entry(purpose) for purpose in purposes]

    # ── Per-entry builder ─────────────────────────────────────────────────────

    def _build_entry(self, purpose: str) -> GeneratedEntry:
        mapping = ACTIVITY_MAP.get(purpose)
        if mapping:
            activity_name, category, default_basis = mapping
        else:
            activity_name = purpose.replace("_", " ").title()
            category = "other"
            default_basis = RopaLegalBasis.LEGITIMATE_INTERESTS

        legal_basis = self._resolve_legal_basis(purpose, default_basis)
        transfer_mechanism = self._resolve_transfer_mechanism()
        requires_dpia = self._resolve_requires_dpia()
        special_condition = self._resolve_special_condition() if self._has_special else None

        return GeneratedEntry(
            activity_name=activity_name,
            purpose=purpose,
            category=category,
            legal_basis=legal_basis,
            data_role=self.data_role,
            data_categories=self.data_categories,
            data_subject_categories=self.data_subject_categories,
            has_special_category_data=self._has_special,
            special_category_types=self._special_types,
            special_category_condition=special_condition,
            has_automated_decision_making=self._has_automated_decisions,
            processing_locations=self._resolve_processing_locations(),
            third_party_transfers={"outside_eea": True} if self._transfers_outside_eea else None,
            transfer_mechanism=transfer_mechanism,
            processors={"uses_processors": True, "tools": self.tech_stack} if self._uses_processors and self.tech_stack else None,
            requires_dpia=requires_dpia,
            security_measures="Technical and organisational measures in place per company security policy.",
        )

    # ── Resolvers ─────────────────────────────────────────────────────────────

    def _resolve_legal_basis(self, purpose: str, default: RopaLegalBasis) -> RopaLegalBasis:
        # If only one lawful basis declared, use it for everything
        if len(self._lawful_bases) == 1:
            return LAWFUL_BASIS_MAP.get(self._lawful_bases[0], default)
        # If multiple declared, check if default is among them
        if self._lawful_bases and default.value in self._lawful_bases:
            return default
        # Fall back to first declared basis, else use per-activity default
        if self._lawful_bases:
            return LAWFUL_BASIS_MAP.get(self._lawful_bases[0], default)
        return default

    def _resolve_processing_locations(self) -> list[str]:
        locations: list[str] = []
        if self.jurisdiction:
            locations.append(self.jurisdiction)
        if self.uses_cloud and self.cloud_providers:
            providers = self.cloud_providers if isinstance(self.cloud_providers, list) else list(self.cloud_providers.keys())
            locations.extend(providers)
        return list(dict.fromkeys(locations))  # dedupe, preserve order

    def _resolve_transfer_mechanism(self) -> TransferMechanism | None:
        if not self._transfers_outside_eea:
            return TransferMechanism.NONE
        # Default to SCCs — most common mechanism; user can update in COM-173 UI
        return TransferMechanism.SCC

    def _resolve_requires_dpia(self) -> bool:
        large_scale = self.number_of_subjects in {"over_100k", "under_100k"}
        return self._has_special and large_scale

    def _resolve_special_condition(self) -> SpecialCategoryCondition:
        # Default to explicit consent — safest starting point; user edits in COM-173
        return SpecialCategoryCondition.EXPLICIT_CONSENT
