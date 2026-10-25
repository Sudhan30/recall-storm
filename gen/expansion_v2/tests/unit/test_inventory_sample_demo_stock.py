"""Unit tests for recallstorm.inventory.sample_demo_stock."""
from recallstorm.inventory.sample_demo_stock import (
    ClubStoreSampleHold,
    DemoStationQuarantine,
    alert_third_party_demo_agency_lead,
    audit_bakery_free_cookie_bins,
    calculate_unbilled_sample_exposure,
    check_pharmacy_immunization_promos,
    clear_demo_station_sanitation_hold,
    halt_active_in_store_sampling_events,
    log_open_package_demo_destruction,
    quarantine_demo_prep_cart_inventory,
    reconcile_expensed_demo_unit_transfers,
    verify_trash_compactor_sample_disposal,
)


def test_sample_demo_stock():
    assert DemoStationQuarantine().status == "ACTIVE"
    assert ClubStoreSampleHold().status == "ACTIVE"
    assert halt_active_in_store_sampling_events("SAMS4735", "FDC1034191")["halted"] is True
    assert quarantine_demo_prep_cart_inventory("SAMS4735", "CART1", 4)["units"] == 4
    assert reconcile_expensed_demo_unit_transfers(10, 3) == 13
    assert alert_third_party_demo_agency_lead("AG1", "SAMS4735")["agency_id"] == "AG1"
    assert verify_trash_compactor_sample_disposal("SAMS4735", True)["disposed"] is True
    assert audit_bakery_free_cookie_bins("WM1", True)["pulled"] is True
    assert check_pharmacy_immunization_promos("WM1", "S1")["promo_sku"] == "S1"
    assert log_open_package_demo_destruction("SAMS4735", 2)["open_units"] == 2
    assert calculate_unbilled_sample_exposure(6, 5.0) == 30.0
    assert clear_demo_station_sanitation_hold("ST1", True)["cleared"] is True
