"""Unit tests for recallstorm.gs1.lots."""
from recallstorm.gs1.lots import (
    date_range_overlap,
    expiry_in_range,
    lot_in_range,
    lot_matches_recall,
    lot_pattern,
    lot_range_from_text,
    normalize_lot,
    parse_lot_code,
    recall_lot_filter,
)


def test_lots_and_date_ranges():
    assert parse_lot_code("Lot # l-2601a") == "L2601A"
    assert normalize_lot("l-2601a") == "L2601A"
    assert lot_pattern("L2601A") == "A9999A"
    assert lot_in_range("L2605", "L2601", "L2610") is True
    assert lot_range_from_text("Lots L2601 through L2610 recalled") == [("L2601", "L2610")]
    assert lot_matches_recall("L2605", ["L9999"], [("L2601", "L2610")]) is True
    assert lot_matches_recall("L2605A", ["L2605*"]) is True
    assert expiry_in_range("2026-11-15", "2026-10-01", "2026-12-31") is True
    assert date_range_overlap(("2026-10-01", "2026-11-01"), ("2026-10-15", "2026-12-01")) is True
    filtered = recall_lot_filter([{"sku_id": "S1", "lot": "L2601A"}, {"sku_id": "S2", "lot": "CLEAN"}], ["L2601A"])
    assert len(filtered) == 1
