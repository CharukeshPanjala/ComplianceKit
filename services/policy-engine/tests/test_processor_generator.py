from app.engine.processor_generator import ProcessorGenerator
from common.models.processor import ProcessorRisk, ProcessorSource, ProcessorStatus, ProcessorTransferMechanism


def make_profile(**kwargs) -> dict:
    return {
        "gdpr_data": {"transfers_outside_eea": False},
        **kwargs,
    }


def make_tool(name: str, category: str = "crm", website_url: str | None = None) -> dict:
    return {"name": name, "category": category, "website_url": website_url}


def test_empty_tools_returns_empty_list():
    results = ProcessorGenerator(make_profile(), []).generate()
    assert results == []


def test_single_tool_generates_one_processor():
    tools = [make_tool("Salesforce", "crm")]
    results = ProcessorGenerator(make_profile(), tools).generate()
    assert len(results) == 1
    p = results[0]
    assert p.name == "Salesforce"
    assert p.category == "crm"


def test_source_is_auto_generated():
    tools = [make_tool("HubSpot", "crm")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.source == ProcessorSource.AUTO_GENERATED


def test_status_defaults_to_active():
    tools = [make_tool("Stripe", "payments")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.status == ProcessorStatus.ACTIVE


def test_dpa_signed_defaults_to_false():
    tools = [make_tool("AWS", "cloud")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.dpa_signed is False


def test_known_category_maps_data_categories():
    tools = [make_tool("Stripe", "payments")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert "financial_data" in p.data_categories
    assert p.risk_level == ProcessorRisk.HIGH


def test_analytics_category_maps_correctly():
    tools = [make_tool("Mixpanel", "analytics")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert "behavioral_data" in p.data_categories
    assert "website_visitors" in p.data_subject_categories
    assert p.risk_level == ProcessorRisk.MEDIUM


def test_unknown_category_uses_defaults():
    tools = [make_tool("SomeTool", "unknown_category")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.data_categories == ["general_data"]
    assert p.risk_level == ProcessorRisk.MEDIUM


def test_no_transfer_mechanism_when_no_eea_transfers():
    tools = [make_tool("Salesforce", "crm")]
    p = ProcessorGenerator(make_profile(gdpr_data={"transfers_outside_eea": False}), tools).generate()[0]
    assert p.transfer_mechanism is None


def test_scc_transfer_mechanism_when_transfers_outside_eea():
    tools = [make_tool("Salesforce", "crm")]
    p = ProcessorGenerator(make_profile(gdpr_data={"transfers_outside_eea": True}), tools).generate()[0]
    assert p.transfer_mechanism == ProcessorTransferMechanism.SCC


def test_deduplicates_tools_by_name():
    tools = [make_tool("Stripe", "payments"), make_tool("Stripe", "payments")]
    results = ProcessorGenerator(make_profile(), tools).generate()
    assert len(results) == 1


def test_deduplication_is_case_insensitive():
    tools = [make_tool("stripe", "payments"), make_tool("Stripe", "payments")]
    results = ProcessorGenerator(make_profile(), tools).generate()
    assert len(results) == 1


def test_multiple_tools_different_categories():
    tools = [
        make_tool("AWS", "cloud"),
        make_tool("Stripe", "payments"),
        make_tool("HubSpot", "crm"),
    ]
    results = ProcessorGenerator(make_profile(), tools).generate()
    assert len(results) == 3
    names = {p.name for p in results}
    assert names == {"AWS", "Stripe", "HubSpot"}


def test_processing_locations_defaults_to_eu():
    tools = [make_tool("Vercel", "cloud")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.processing_locations == ["European Union"]


def test_cloud_category_is_high_risk():
    tools = [make_tool("AWS", "cloud")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.risk_level == ProcessorRisk.HIGH


def test_hr_category_is_high_risk():
    tools = [make_tool("BambooHR", "hr")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.risk_level == ProcessorRisk.HIGH


def test_devtools_category_is_low_risk():
    tools = [make_tool("GitHub", "devtools")]
    p = ProcessorGenerator(make_profile(), tools).generate()[0]
    assert p.risk_level == ProcessorRisk.LOW
