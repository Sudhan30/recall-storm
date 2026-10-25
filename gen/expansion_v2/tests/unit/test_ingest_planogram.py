"""Unit tests for recallstorm.ingest.planogram."""
from contract import Sku, StoreFormat
from recallstorm.ingest.planogram import (
    bay_capacity,
    facing_units_estimate,
    location_from_code,
    merge_planograms,
    parse_planogram_row,
    planogram_diff,
    planogram_to_facings,
    shelf_positions,
    validate_planogram,
)


def test_planogram_functions():
    loc = location_from_code("A02-3-4-5")
    assert loc.aisle == "A02" and loc.bay == 3
    f1 = parse_planogram_row({"store_id": "WM1", "sku_id": "S1", "loc_code": "A02-3-4-5", "units": 12})
    f2 = parse_planogram_row({"store_id": "WM1", "sku_id": "S1", "loc_code": "A02-3-4-5", "units": 8})
    merged = merge_planograms([f1], [f2])
    assert len(merged) == 1 and merged[0].units == 20
    assert bay_capacity(1, 1) == 48
    assert len(shelf_positions(merged, "A02", 3)) == 1
    assert planogram_diff([f1], [])["removed"] == 1
    sku = Sku("S1", "00012345678905", "N", "B", "c", "I", True, False, 12, 1.0, 5.0)
    assert facing_units_estimate(sku, StoreFormat.SAMS) == 36
    assert len(planogram_to_facings([{"store_id": "WM1", "sku_id": "S1"}])) == 1
    assert validate_planogram(merged) == []
