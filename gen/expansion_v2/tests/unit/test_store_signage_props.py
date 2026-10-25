"""Property tests for recallstorm.store.signage."""
from contract import Location
from recallstorm.store.signage import printer_queue


def test_printer_queue_sorting_props():
    tags = [
        {"store_id": "WM1", "loc": {"aisle": f"A{i:02d}", "bay": b, "shelf": 1, "pos": 1}}
        for i in (5, 1, 3)
        for b in (4, 2)
    ]
    q = printer_queue(tags)
    keys = [(t["loc"]["aisle"], t["loc"]["bay"]) for t in q]
    assert keys == sorted(keys)
