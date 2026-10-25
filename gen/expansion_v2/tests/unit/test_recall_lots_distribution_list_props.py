"""Property tests for recallstorm.recall_lots.distribution_list."""
from recallstorm.recall_lots.distribution_list import rank_stores_by_shipment_volume


def test_rank_stores_tie_break_determinism():
    vols = {f"WM{i:03d}": 10 for i in range(15)}
    assert rank_stores_by_shipment_volume(vols) == sorted(vols.keys())
