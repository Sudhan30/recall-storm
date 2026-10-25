"""Unit tests for recallstorm.gs1.lots."""
from datetime import date
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


def test_gs1_lots():
    assert normalize_lot("Lot: L-2601-A") == "L2601A"
    assert parse_lot_code("BATCH 99") == "99"
    assert lot_in_range("L2605", "L2601", "L2610") is True
    assert lot_in_range("L2620", "L2601", "L2610") is False
    assert lot_range_from_text("Lots L2601 through L2610") == [("L2601", "L2610")]
    assert lot_pattern("L26*").match("L2605") is not None
    recall_specs = ["L2601..L2610", "B99*", "EXACT1"]
    assert lot_matches_recall("L2604", recall_specs) is True
    assert lot_matches_recall("B99123", recall_specs) is True
    assert lot_matches_recall("EXACT1", recall_specs) is True
    assert lot_matches_recall("SAFE1", recall_specs) is False
    assert recall_lot_filter(["L2604", "SAFE1"], recall_specs) == ["L2604"]
    d1, d2, d3 = date(2026, 1, 1), date(2026, 6, 1), date(2026, 12, 1)
    assert expiry_in_range(d2, d1, d3) is True
    assert date_range_overlap((d1, d2), (d2, d3)) is True
