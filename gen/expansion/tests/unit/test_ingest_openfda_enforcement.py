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


def test_openfda_enforcement_parsing():
    raw = {
        "recall_number": "F-0100-2026",
        "status": "Ongoing",
        "classification": "Class II",
        "product_description": "Rainbow Sprinkles UPC 07502264930572",
        "code_info": "Lot: L2601A, Batch B9920; Best by 2026-10-01 to 2026-12-31",
        "reason_for_recall": "Contains prohibited FD&C Red No. 3",
        "distribution_pattern": "CA, NV, OR",
        "report_date": "2026-12-15",
    }
    assert extract_lot_codes(raw["code_info"]) == ["L2601A", "B9920"]
    assert extract_date_ranges(raw["code_info"]) == [("2026-10-01", "2026-12-31")]
    assert extract_product_gtins(raw["product_description"]) == ["07502264930572"]
    assert classify_recall_reason(raw["reason_for_recall"]) == "PROHIBITED_ADDITIVE"
    assert recall_jurisdictions(raw["distribution_pattern"]) == ["CA", "NV", "OR"]
    assert recall_status(raw) == "ONGOING"
    parsed = parse_enforcement_report(raw)
    assert parsed["recall_id"] == "F-0100-2026"
    rec = enforcement_to_recall(raw)
    assert rec["source"] == "OPENFDA"
    pages = [{"results": [raw]}]
    assert len(list(iter_enforcement_pages(pages))) == 1
