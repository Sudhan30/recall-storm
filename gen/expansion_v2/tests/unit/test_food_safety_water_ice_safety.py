"""Unit tests for recallstorm.food_safety.water_ice_safety."""
from recallstorm.food_safety.water_ice_safety import (
    BoilWaterAdvisoryResponse,
    IceMachineSanitation,
    audit_seafood_ice_flaker_swabs,
    authorize_water_system_reopen,
    disable_produce_misting_systems,
    generate_food_prep_shutdown_checklist,
    lock_fountain_beverage_dispensers,
    map_utility_boil_water_polygons,
    quarantine_packaged_store_ice,
    schedule_carbon_filter_replacement,
    track_post_advisory_line_flushing,
    verify_potable_water_tanker_coa,
)


def test_water_ice_safety():
    assert BoilWaterAdvisoryResponse().status == "ACTIVE"
    assert IceMachineSanitation().status == "ACTIVE"
    assert map_utility_boil_water_polygons(["90210", "90211"], "90210") is True
    assert disable_produce_misting_systems("WM1")["misting_off"] is True
    assert quarantine_packaged_store_ice("WM1", 40)["bags"] == 40
    assert lock_fountain_beverage_dispensers("WM1")["locked"] is True
    assert schedule_carbon_filter_replacement("WM1", 4)["filters"] == 4
    assert verify_potable_water_tanker_coa("TNK1", True)["approved"] is True
    assert track_post_advisory_line_flushing("WM1", 15.0)["sufficient"] is True
    assert audit_seafood_ice_flaker_swabs("WM1", True)["passed"] is True
    assert len(generate_food_prep_shutdown_checklist("WM1")["steps"]) == 3
    assert authorize_water_system_reopen("WM1", True, True)["reopened"] is True
