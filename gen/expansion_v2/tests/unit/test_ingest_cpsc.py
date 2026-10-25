"""Unit tests for recallstorm.ingest.cpsc."""
from recallstorm.ingest.cpsc import (
    cpsc_dates,
    cpsc_hazard_text,
    cpsc_is_food_contact,
    cpsc_product_names,
    cpsc_remedy,
    cpsc_to_recall,
    cpsc_units,
    cpsc_upcs,
    parse_cpsc_recall,
)


def test_cpsc_parsing():
    item = {
        "RecallNumber": "26-101",
        "RecallDate": "2026-03-15",
        "LastPublishDate": "2026-03-16",
        "Products": [{"Name": "Nonstick Frying Pan Cookware", "NumberOfUnits": "About 15,000"}],
        "UPCs": [{"UPC": "012345678905"}],
        "Hazards": [{"Name": "PFAS coating degradation"}],
        "Remedies": [{"Name": "Full refund"}],
    }
    assert cpsc_product_names(item) == ["Nonstick Frying Pan Cookware"]
    assert cpsc_upcs(item) == ["00012345678905"]
    assert "PFAS" in cpsc_hazard_text(item)
    assert cpsc_remedy(item) == "Full refund"
    assert cpsc_dates(item) == ("2026-03-15", "2026-03-16")
    assert cpsc_units(item) == 15000
    assert cpsc_is_food_contact(item) is True
    parsed = parse_cpsc_recall(item)
    assert parsed["recall_number"] == "26-101"
    rec = cpsc_to_recall(item)
    assert rec["recall_id"] == "CPSC-26-101"
