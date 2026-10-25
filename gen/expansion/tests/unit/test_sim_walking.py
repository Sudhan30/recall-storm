"""Unit tests for recallstorm.sim.walking."""
from datetime import datetime, timezone
from contract import Location
from recallstorm.sim.walking import (
    WalkModel,
    aisle_graph,
    congestion_penalty,
    path_to_moves,
    shortest_path,
    speed_for_associate,
    walk_path,
    walk_seconds,
    walking_summary,
)


def test_walking_simulation():
    wm = WalkModel()
    assert wm.speed_fps == 4.0
    assert speed_for_associate(False) == 4.0
    assert speed_for_associate(True) == 3.6
    assert congestion_penalty(3) == 1.1

    l1 = Location("A01", 1, 1, 1)
    l2 = Location("A01", 5, 1, 1)
    l3 = Location("A02", 3, 1, 1)
    assert walk_seconds(l1, l2) == 4.0
    assert walk_path([l3, l2, l1])[0] == l1
    assert "A01" in aisle_graph([l1, l2])
    sp = shortest_path(l1, l3)
    assert len(sp) == 3
    moves = path_to_moves(sp, "WM1", "A1", datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc), "TSK-1")
    assert len(moves) == 3 and moves[0]["kind"] == "MOVE"
    assert walking_summary([l1, l2])["total_distance_ft"] == 16.0
