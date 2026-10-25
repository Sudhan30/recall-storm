"""Unit tests for recallstorm.states.wa_pfas_packaging."""
from recallstorm.states.wa_pfas_packaging import (
    PlantFiberWrapperCheck,
    WaPfasPackagingBan,
    audit_wa_bakery_clam_shells,
    calculate_wa_packaging_fines,
    check_wa_deli_paper_lots,
    evaluate_wa_compostable_claim,
    filter_wa_in_store_prep_wraps,
    flag_wa_greaseproof_containers,
    generate_wa_pfas_certificate,
    map_wa_fresh_dept_packaging,
    test_wa_fluorine_ppm_limit as run_fluorine_check,
    verify_wa_alternative_assessment,
)


def test_wa_pfas_packaging():
    assert WaPfasPackagingBan().status == "ACTIVE"
    assert PlantFiberWrapperCheck().status == "ACTIVE"
    assert run_fluorine_check(150.0, 100.0)["prohibited"] is True
    assert evaluate_wa_compostable_claim("BPI Compostable", 20.0)["valid"] is True
    assert check_wa_deli_paper_lots("LOT1")["cleared"] is True
    assert flag_wa_greaseproof_containers("Fluoro-treated fiber")["flagged"] is True
    assert verify_wa_alternative_assessment("wrappers")["ban_active"] is True
    assert "DELI" in map_wa_fresh_dept_packaging("WM1")["depts"]
    assert calculate_wa_packaging_fines(2, 5000.0) == 10000.0
    assert audit_wa_bakery_clam_shells("WM1", 4)["cases"] == 4
    assert generate_wa_pfas_certificate("V1", "S1")["vendor_id"] == "V1"
    assert filter_wa_in_store_prep_wraps(["W2", "W1"]) == ["W1", "W2"]
