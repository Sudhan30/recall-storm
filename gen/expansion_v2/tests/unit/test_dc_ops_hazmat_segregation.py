"""Unit tests for recallstorm.dc_ops.hazmat_segregation."""
from recallstorm.dc_ops.hazmat_segregation import (
    HazmatQuarantineProtocol,
    RcraWasteClassifier,
    assign_un_number_and_packing_group_labels,
    audit_dc_tier_ii_epcra_reporting_thresholds,
    check_oxidizer_vs_corrosive_incompatibility,
    classify_recalled_sku_by_dot_hazard_class,
    coordinate_clean_harbors_lab_pack_pickup,
    generate_epa_hazardous_waste_manifest,
    monitor_lithium_battery_thermal_runaway_risk,
    segregate_flammable_aerosols_in_wire_cage,
    track_acute_hazardous_waste_p_list_limits,
    verify_spill_containment_berm_capacity,
)


def test_hazmat_segregation():
    assert HazmatQuarantineProtocol().status == "ACTIVE"
    assert RcraWasteClassifier().status == "ACTIVE"
    assert classify_recalled_sku_by_dot_hazard_class("multi-purpose lubricant spray") == "2.1_AEROSOL"
    assert segregate_flammable_aerosols_in_wire_cage("DC1", 25)["nfpa_30b_cage"] is True
    assert check_oxidizer_vs_corrosive_incompatibility("ACID", "BLEACH")["incompatible"] is True
    assert assign_un_number_and_packing_group_labels("2.1_AEROSOL")["un_number"] == "UN1950"
    assert monitor_lithium_battery_thermal_runaway_risk(60.0, 45.0)["thermal_alert"] is True
    assert verify_spill_containment_berm_capacity(55.0, 200.0, 75.0)["compliant"] is True
    assert generate_epa_hazardous_waste_manifest("CAR0001", ["D001"])["waste_codes"] == ["D001"]
    assert coordinate_clean_harbors_lab_pack_pickup("WM1", 2)["drums"] == 2
    assert track_acute_hazardous_waste_p_list_limits(1.5, 1.0)["lqg_triggered"] is True
    assert audit_dc_tier_ii_epcra_reporting_thresholds(12000.0, 10000.0)["reportable"] is True
