"""Unit tests for recallstorm.ingest.openfda_enforcement."""
from recallstorm.ingest.openfda_enforcement import (
    classify_recall_reason,
    enforcement_to_recall,
    extract_date_ranges,
    extract_lot_codes,
    extract_product_gtins,
    iter_enforcement_pages,
    parse_enforcement_report,
    recall_jurisdictions,
    recall_status,
)


def test_openfda_enforcement():
    rep = {
        "recall_number": "F-0123-2026",
        "classification": "Class I",
        "status": "Ongoing",
        "product_description": "Rainbow Sprinkles UPC 07502264930572",
        "code_info": "Lot: L2601A and Lot: L2602B, Best By 2026-05-01 to 2026-09-01",
        "reason_for_recall": "Contains unapproved FD&C Red No. 3 additive",
        "distribution_pattern": "CA, NV, OR",
    }
    parsed = parse_enforcement_report(rep)
    assert parsed["lots"] == ["L2601A", "L2602B"]
    assert parsed["date_ranges"] == [("2026-05-01", "2026-09-01")]
    assert parsed["gtins"] == ["07502264930572"]
    assert parsed["reason_class"] == "ADDITIVE"
    assert parsed["jurisdictions"] == ["CA", "NV", "OR"]
    assert recall_status(rep) == "Ongoing"
    rec = enforcement_to_recall(rep)
    assert rec["recall_id"] == "F-0123-2026"
    assert len(iter_enforcement_pages([{"results": [rep]}])) == 1
    assert classify_recall_reason("Undeclared peanut") == "ALLERGEN"
    assert recall_jurisdictions("Nationwide") == ["US"]
    assert extract_lot_codes("") == []
    assert extract_date_ranges("") == []
    assert extract_product_gtins("") == []
