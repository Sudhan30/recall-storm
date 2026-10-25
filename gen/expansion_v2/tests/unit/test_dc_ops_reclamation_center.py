"""Unit tests for recallstorm.dc_ops.reclamation_center."""
from recallstorm.dc_ops.reclamation_center import (
    CrushedBaleTracker,
    ReclamationSortEngine,
    audit_store_return_tote_manifest_accuracy,
    calculate_reclamation_processing_cost_per_unit,
    configure_reclamation_scanner_sort_chutes,
    generate_vendor_pickup_ready_notification,
    prevent_recalled_item_from_salvage_auction,
    record_zero_value_trash_compactor_throws,
    route_scanned_returns_to_vendor_gaylords,
    separate_hazmat_aerosols_and_lithium_ion,
    verify_item_eligibility_for_food_bank_donate,
    weigh_and_tag_completed_vendor_pallets,
)


def test_reclamation_center():
    assert ReclamationSortEngine().status == "ACTIVE"
    assert CrushedBaleTracker().status == "ACTIVE"
    assert configure_reclamation_scanner_sort_chutes("S1", "DESTROY") == "CHUTE_COMPACTOR_DESTROY"
    assert route_scanned_returns_to_vendor_gaylords("V1", 50)["units"] == 50
    sep = separate_hazmat_aerosols_and_lithium_ion([{"sku_id": "H1", "is_hazmat": True}, {"sku_id": "G1", "is_hazmat": False}])
    assert sep["hazmat"] == ["H1"] and sep["general"] == ["G1"]
    assert weigh_and_tag_completed_vendor_pallets("GAY1", 450.0)["weight_lb"] == 450.0
    assert record_zero_value_trash_compactor_throws("S1", 20)["units"] == 20
    assert verify_item_eligibility_for_food_bank_donate(True)["donate_allowed"] is False
    assert prevent_recalled_item_from_salvage_auction("S1")["salvage_blocked"] is True
    assert audit_store_return_tote_manifest_accuracy(100, 100)["accurate"] is True
    assert calculate_reclamation_processing_cost_per_unit(250.0, 1000) == 0.25
    assert generate_vendor_pickup_ready_notification("V1", 4)["pallet_count"] == 4
