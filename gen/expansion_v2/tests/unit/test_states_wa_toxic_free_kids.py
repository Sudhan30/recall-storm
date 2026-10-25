"""Unit tests for recallstorm.states.wa_toxic_free_kids."""
from recallstorm.states.wa_toxic_free_kids import (
    HighPriorityChemicalList,
    WaTfkcaRule,
    build_wa_Ecology_declaration,
    calculate_wa_de_minimis_threshold,
    check_wa_phthalates_ppm,
    evaluate_wa_childrens_product,
    filter_wa_baby_aisle_skus,
    flag_wa_bisphenol_packaging,
    generate_wa_recall_directive,
    parse_wa_cspa_notice_list,
    validate_wa_supplier_assay,
    verify_wa_ecology_reporting,
)


def test_wa_toxic_free_kids():
    assert WaTfkcaRule().status == "ACTIVE"
    assert HighPriorityChemicalList().status == "ACTIVE"
    assert check_wa_phthalates_ppm(1500.0)["violation"] is True
    assert evaluate_wa_childrens_product("toy", 36)["in_scope"] is True
    assert verify_wa_ecology_reporting("V1", True)["compliant"] is True
    assert calculate_wa_de_minimis_threshold(120.0, 100.0)["reportable"] is True
    assert flag_wa_bisphenol_packaging("Epoxy BPA lining")["flagged"] is True
    assert parse_wa_cspa_notice_list("N1")["state"] == "WA"
    assert build_wa_Ecology_declaration("S1")["sku_id"] == "S1"
    assert filter_wa_baby_aisle_skus(["B2", "B1"]) == ["B1", "B2"]
    assert validate_wa_supplier_assay("L1", True)["passed"] is True
    assert generate_wa_recall_directive("WM1", "S1")["store_id"] == "WM1"
