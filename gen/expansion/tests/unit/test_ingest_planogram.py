"""Unit tests for recallstorm.ingest.planogram."""
from contract import StoreFormat
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
    loc = location_from_code("A01-B2-S3-P4")
    assert loc.aisle == "A01" and loc.bay == 2 and loc.shelf == 3 and loc.pos == 4
    assert bay_capacity(loc) == 36
    assert len(shelf_positions("A01", 1, 2, 3)) == 6

    row = {"store_id": "WM1563", "sku_id": "FDC1034191", "loc_code": "A01-B1-S1-P1", "units": 10}
    parsed = parse_planogram_row(row)
    facings = planogram_to_facings([parsed])
    assert validate_planogram(facings) == []
    merged = merge_planograms(facings, facings)
    assert merged[0].units == 20
    diff = planogram_diff([], facings)
    assert len(diff["added"]) == 1
    assert facing_units_estimate(StoreFormat.SAMS, "candy") == 30
