"""Unit tests for recallstorm.sim.walking."""
from datetime import datetime
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


def test_sim_walking():
    l1 = Location("A01", 1, 1, 1)
    l2 = Location("A02", 3, 1, 1)
    assert speed_for_associate(True) > speed_for_associate(False)
    assert congestion_penalty(1) == 1.0 and congestion_penalty(3) == 0.8
    assert walk_seconds(l1, l2) > 0.0
    assert walk_path([l2, l1]) == [l1, l2]
    assert "A01" in aisle_graph([l1, l2])
    assert shortest_path(l1, l2) == [l1, l2]
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    moves = path_to_moves("WM1", "A1", "T1", [l1, l2], t0)
    assert len(moves) == 2 and moves[0]["kind"] == "MOVE"
    assert walking_summary([l1, l2])["stops"] == 2
    assert WalkModel().base_speed_mps == 1.2
