from dataclasses import dataclass

from common.models.processor import ProcessorRisk, ProcessorSource, ProcessorStatus, ProcessorTransferMechanism


# ── Category → processing detail mapping ──────────────────────────────────────

# category → (data_categories, data_subject_categories, risk_level)
CATEGORY_MAP: dict[str, tuple[list[str], list[str], ProcessorRisk]] = {
    "cloud":            (["all_data_types"],                          ["customers", "employees"],     ProcessorRisk.HIGH),
    "payments":         (["financial_data", "contact_data"],          ["customers"],                  ProcessorRisk.HIGH),
    "crm":              (["contact_data", "behavioral_data"],         ["customers", "prospects"],     ProcessorRisk.MEDIUM),
    "email":            (["contact_data", "communication_data"],      ["customers", "employees"],     ProcessorRisk.MEDIUM),
    "analytics":        (["behavioral_data", "usage_data", "ip_addresses"], ["website_visitors"],    ProcessorRisk.MEDIUM),
    "hr":               (["hr_data", "identification_data", "contact_data"], ["employees"],          ProcessorRisk.HIGH),
    "support":          (["contact_data", "communication_data"],      ["customers"],                  ProcessorRisk.MEDIUM),
    "auth":             (["identification_data", "ip_addresses"],     ["customers", "employees"],     ProcessorRisk.MEDIUM),
    "storage":          (["all_data_types"],                          ["customers", "employees"],     ProcessorRisk.HIGH),
    "monitoring":       (["technical_data", "ip_addresses"],          ["employees", "customers"],     ProcessorRisk.LOW),
    "communication":    (["contact_data", "communication_data"],      ["employees", "customers"],     ProcessorRisk.MEDIUM),
    "finance":          (["financial_data", "identification_data"],   ["employees"],                  ProcessorRisk.HIGH),
    "sales":            (["contact_data", "behavioral_data"],         ["prospects", "customers"],     ProcessorRisk.MEDIUM),
    "recruitment":      (["identification_data", "hr_data"],          ["job_applicants"],             ProcessorRisk.MEDIUM),
    "eor":              (["hr_data", "financial_data", "identification_data"], ["employees"],         ProcessorRisk.HIGH),
    "security":         (["technical_data", "ip_addresses", "behavioral_data"], ["employees", "customers"], ProcessorRisk.MEDIUM),
    "devtools":         (["technical_data"],                          ["employees"],                  ProcessorRisk.LOW),
    "devops":           (["technical_data"],                          ["employees"],                  ProcessorRisk.LOW),
    "bi":               (["behavioral_data", "usage_data"],           ["customers", "employees"],     ProcessorRisk.MEDIUM),
    "cms":              (["contact_data", "behavioral_data"],         ["website_visitors"],           ProcessorRisk.LOW),
    "automation":       (["contact_data", "behavioral_data"],         ["customers"],                  ProcessorRisk.MEDIUM),
    "feedback":         (["contact_data", "behavioral_data"],         ["customers"],                  ProcessorRisk.LOW),
    "seo":              (["behavioral_data", "ip_addresses"],         ["website_visitors"],           ProcessorRisk.LOW),
    "social-ads":       (["behavioral_data", "contact_data"],         ["website_visitors", "customers"], ProcessorRisk.MEDIUM),
    "customer-success": (["contact_data", "behavioral_data"],         ["customers"],                  ProcessorRisk.MEDIUM),
    "data-enrichment":  (["contact_data", "identification_data"],     ["prospects", "customers"],     ProcessorRisk.HIGH),
    "expense":          (["financial_data", "identification_data"],   ["employees"],                  ProcessorRisk.MEDIUM),
    "video":            (["contact_data", "behavioral_data"],         ["employees", "customers"],     ProcessorRisk.LOW),
    "legal":            (["identification_data", "contact_data"],     ["customers", "employees"],     ProcessorRisk.MEDIUM),
    "feature-flags":    (["behavioral_data", "identification_data"],  ["customers"],                  ProcessorRisk.LOW),
}

DEFAULT_CATEGORY_DATA = (["general_data"], ["customers", "employees"], ProcessorRisk.MEDIUM)


# ── Result dataclass (unsaved) ────────────────────────────────────────────────

@dataclass
class GeneratedProcessor:
    name: str
    category: str | None
    data_categories: list[str]
    data_subject_categories: list[str]
    processing_locations: list[str]
    risk_level: ProcessorRisk
    status: ProcessorStatus
    source: ProcessorSource
    dpa_signed: bool
    transfer_mechanism: ProcessorTransferMechanism | None


# ── Engine ────────────────────────────────────────────────────────────────────

class ProcessorGenerator:

    def __init__(self, profile: dict, tools: list[dict]):
        """
        profile: serialised CompanyProfile dict
        tools:   list of SaasTool dicts matching the profile's tech_stack tool names
        """
        self.profile = profile
        self.tools = tools
        self._transfers_outside_eea: bool = (
            (profile.get("gdpr_data") or {}).get("transfers_outside_eea", False)
        )

    def generate(self) -> list[GeneratedProcessor]:
        seen: set[str] = set()
        results: list[GeneratedProcessor] = []
        for tool in self.tools:
            name = tool.get("name", "").strip()
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            results.append(self._build(tool))
        return results

    def _build(self, tool: dict) -> GeneratedProcessor:
        category = tool.get("category") or "other"
        data_cats, subject_cats, risk = CATEGORY_MAP.get(category, DEFAULT_CATEGORY_DATA)

        transfer_mechanism = None
        if self._transfers_outside_eea:
            transfer_mechanism = ProcessorTransferMechanism.SCC

        return GeneratedProcessor(
            name=tool.get("name", ""),
            category=category,
            data_categories=list(data_cats),
            data_subject_categories=list(subject_cats),
            processing_locations=["European Union"],
            risk_level=risk,
            status=ProcessorStatus.ACTIVE,
            source=ProcessorSource.AUTO_GENERATED,
            dpa_signed=False,
            transfer_mechanism=transfer_mechanism,
        )
