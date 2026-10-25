"""Unit tests for recallstorm.recall_lots.fda_notice_parser."""
from recallstorm.recall_lots.fda_notice_parser import (
    ExtractedRecallMetadata,
    FdaEnforcementNotice,
    detect_undeclared_allergen_type,
    extract_recalling_firm_feis,
    extract_upc_list_from_text,
    identify_fda_recall_class,
    link_fda_res_event_number,
    normalize_fda_code_info_block,
    parse_fda_press_release_html,
    parse_fda_reason_for_recall,
    split_multi_brand_table,
    validate_parsed_notice_schema,
)


def test_fda_notice_parser():
    assert FdaEnforcementNotice().status == "ACTIVE"
    assert ExtractedRecallMetadata().status == "ACTIVE"
    assert parse_fda_press_release_html("<p>Urgent Recall</p>")["text"] == "Urgent Recall"
    assert extract_recalling_firm_feis("Firm FEI: 3001234567") == ["3001234567"]
    assert identify_fda_recall_class("Classified as Class I recall") == "Class I"
    assert parse_fda_reason_for_recall("Red 3")["reason"] == "Red 3"
    assert extract_upc_list_from_text("UPC 073621007017") == ["00073621007017"]
    assert normalize_fda_code_info_block("lot   a1") == "LOT A1"
    assert "B1" in split_multi_brand_table([{"brand": "B1", "sku": "S1"}])
    assert detect_undeclared_allergen_type("Contains undeclared peanut") == "PEANUT"
    assert link_fda_res_event_number("RES-99", "F-001")["event_id"] == "RES-99"
    assert validate_parsed_notice_schema({"recall_number": "F-001"})["valid"] is True
