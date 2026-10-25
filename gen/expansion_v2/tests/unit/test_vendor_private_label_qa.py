"""Unit tests for recallstorm.vendor.private_label_qa."""
from recallstorm.vendor.private_label_qa import (
    CoPackerAuditTracker,
    OwnBrandRecallManager,
    access_tracegains_supplier_spec_portal,
    coordinate_private_label_press_release,
    enforce_own_brand_zero_tolerance_policy,
    manage_packaging_film_write_off_liability,
    map_private_label_sku_to_copacker_plant,
    quarantine_shared_line_national_brand_runs,
    review_copacker_environmental_swab_trends,
    score_copacker_food_safety_culture,
    track_capa_corrective_action_closure,
    trigger_unannounced_gfSI_sqf_audit,
)


def test_private_label_qa():
    assert OwnBrandRecallManager().status == "ACTIVE"
    assert CoPackerAuditTracker().status == "ACTIVE"
    assert map_private_label_sku_to_copacker_plant("FDC2524922", "PLT1")["plant_id"] == "PLT1"
    assert access_tracegains_supplier_spec_portal("FDC2524922")["spec_found"] is True
    assert trigger_unannounced_gfSI_sqf_audit("PLT1", 92)["passed"] is True
    assert quarantine_shared_line_national_brand_runs("L1", ["S1"])["sibling_skus"] == ["S1"]
    assert review_copacker_environmental_swab_trends("PLT1", 1)["hold_plant"] is True
    assert enforce_own_brand_zero_tolerance_policy("FDC2524922", True)["pull"] is True
    assert coordinate_private_label_press_release("FDC2524922", "Great Value")["brand"] == "Great Value"
    assert manage_packaging_film_write_off_liability(10, 250.0) == 2500.0
    assert track_capa_corrective_action_closure("CAPA1", True)["closed"] is True
    assert score_copacker_food_safety_culture(95.0, False) == 75.0
