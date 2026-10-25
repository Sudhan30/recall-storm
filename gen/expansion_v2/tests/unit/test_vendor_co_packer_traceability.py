"""Unit tests for recallstorm.vendor.co_packer_traceability."""
from recallstorm.vendor.co_packer_traceability import (
    MultiCoPackerResolver,
    PlantCodeRouter,
    audit_unauthorized_subcontracting_events,
    clear_unaffected_sister_plant_inventory,
    decode_julian_plant_suffix_on_packaging,
    generate_plant_specific_shelf_pull_rules,
    isolate_affected_co_packer_facility,
    map_regional_co_packer_dc_assignments,
    reconcile_packaging_roll_stock_transfers,
    update_gtin_to_plant_routing_tables,
    validate_dual_sourced_sku_segregation,
    verify_co_packer_sub_ingredient_suppliers,
)


def test_co_packer_traceability():
    assert MultiCoPackerResolver().status == "ACTIVE"
    assert PlantCodeRouter().status == "ACTIVE"
    assert decode_julian_plant_suffix_on_packaging("26145CA")["plant_suffix"] == "CA"
    lots = ["26145CA", "26145TX"]
    assert isolate_affected_co_packer_facility(lots, "CA") == ["26145CA"]
    assert clear_unaffected_sister_plant_inventory(lots, "CA") == ["26145TX"]
    assert map_regional_co_packer_dc_assignments({"PLT1": ["DC_NORTH"]}, "PLT1") == ["DC_NORTH"]
    assert verify_co_packer_sub_ingredient_suppliers("PLT1", ["SUP1"])["suppliers"] == ["SUP1"]
    assert audit_unauthorized_subcontracting_events("PLT1", "PLT2")["unauthorized"] is True
    assert reconcile_packaging_roll_stock_transfers("PLT1", "PLT2", 4)["rolls"] == 4
    assert update_gtin_to_plant_routing_tables("07502264930572", "PLT2")["backup_plant"] == "PLT2"
    assert generate_plant_specific_shelf_pull_rules("S1", "CA")["plant_suffix"] == "CA"
    assert validate_dual_sourced_sku_segregation(True)["segregated"] is True
