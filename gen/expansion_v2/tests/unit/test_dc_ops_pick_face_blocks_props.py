"""Property tests for recallstorm.dc_ops.pick_face_blocks."""
from recallstorm.dc_ops.pick_face_blocks import cancel_pending_letdown_replenishment_tasks


def test_cancel_letdowns_sorted_props():
    ids = [f"LET-{i:02d}" for i in (9, 2, 7, 1, 5)]
    assert cancel_pending_letdown_replenishment_tasks(ids) == sorted(ids)
