"""Unit tests for recallstorm.inventory.lot_level_perpetual."""
from recallstorm.inventory.lot_level_perpetual import (
    FefoDepletionModel,
    LotSubLedgerEngine,
    bound_lot_presence_probability,
    estimate_lot_on_hand_by_receipt_date,
    export_store_lot_exposure_range,
    identify_stale_unrotated_lot_layers,
    ingest_epcis_case_depletion_events,
    model_fefo_customer_depletion_curve,
    reconcile_mixed_lot_shelf_bins,
    track_backroom_case_lot_tags,
    update_lot_balance_from_pull_scan,
    validate_lot_subledger_integrity,
)


def test_lot_level_perpetual():
    assert LotSubLedgerEngine().status == "ACTIVE"
    assert FefoDepletionModel().status == "ACTIVE"
    assert estimate_lot_on_hand_by_receipt_date(20, 5, 2.0) == 10
    assert model_fefo_customer_depletion_curve(10, 2, 3.0) == [10, 7, 4]
    assert ingest_epcis_case_depletion_events("L1", 3)["cases"] == 3
    assert bound_lot_presence_probability(5, 20) == 0.25
    assert reconcile_mixed_lot_shelf_bins({"L1": 4, "L2": 6})["total_units"] == 10
    assert update_lot_balance_from_pull_scan("L1", 10, 4) == 6
    assert track_backroom_case_lot_tags("WM1", ["L2", "L1"])["lots"] == ["L1", "L2"]
    assert identify_stale_unrotated_lot_layers(["2026-01-01", "2026-12-01"], "2026-06-01") == ["2026-01-01"]
    assert export_store_lot_exposure_range(2, 10)["max"] == 10
    assert validate_lot_subledger_integrity({"L1": 4, "L2": 6}, 10) is True
