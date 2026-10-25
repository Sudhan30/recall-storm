"""Unit tests for recallstorm.recall_lots.fsis_notice_parser."""
from recallstorm.recall_lots.fsis_notice_parser import (
    EstNumberExtractor,
    FsisRecallRelease,
    classify_fsis_health_hazard_level,
    extract_fsis_case_code_strings,
    extract_usda_inspection_mark,
    identify_fsis_import_country,
    match_fsis_retail_consignee_pdf,
    normalize_usda_product_title,
    parse_fsis_establishment_code,
    parse_fsis_poultry_serial_range,
    parse_fsis_production_date_span,
    validate_fsis_notice_completeness,
)


def test_fsis_notice_parser():
    assert FsisRecallRelease().status == "ACTIVE"
    assert EstNumberExtractor().status == "ACTIVE"
    assert parse_fsis_establishment_code("Inside mark EST. 1234M") == "EST.1234M"
    assert extract_usda_inspection_mark("P-450")["est"] == "P-450"
    assert classify_fsis_health_hazard_level("Class I High Health Risk") == "HIGH"
    assert parse_fsis_production_date_span("2026-01-01", "2026-01-05")["start"] == "2026-01-01"
    assert extract_fsis_case_code_strings("Case: C-901 and Case: C-902") == ["C-901", "C-902"]
    assert identify_fsis_import_country("Imported from Brazil") == "BRAZIL"
    assert match_fsis_retail_consignee_pdf("Walmart", "Shipped to Walmart Supercenter")["matched"] is True
    assert normalize_usda_product_title("  beef   patties ") == "BEEF PATTIES"
    assert parse_fsis_poultry_serial_range(10, 12) == ["P-10", "P-11", "P-12"]
    assert validate_fsis_notice_completeness({"recall_number": "010-2026"})["valid"] is True
