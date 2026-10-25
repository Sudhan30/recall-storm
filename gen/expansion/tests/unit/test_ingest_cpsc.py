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
    raw = {
        "RecallNumber": "26-099",
        "RecallDate": "2026-11-20T00:00:00",
        "LastPublishDate": "2026-11-21T00:00:00",
        "Products": [{"Name": "Nonstick Cookware Skillet", "UPC": "012345678905", "NumberOfUnits": "About 15,000"}],
        "Hazards": [{"Name": "PFAS coating delamination"}],
        "Remedies": [{"Name": "Full refund"}],
    }
    assert cpsc_product_names(raw) == ["Nonstick Cookware Skillet"]
    assert cpsc_upcs(raw) == ["00012345678905"]
    assert cpsc_hazard_text(raw) == "PFAS coating delamination"
    assert cpsc_remedy(raw) == "Full refund"
    assert cpsc_dates(raw) == ("2026-11-20", "2026-11-21")
    assert cpsc_units(raw) == 15000
    assert cpsc_is_food_contact(raw) is True
    parsed = parse_cpsc_recall(raw)
    assert parsed["recall_id"] == "CPSC-26-099"
    rec = cpsc_to_recall(raw)
    assert rec["source"] == "CPSC"
