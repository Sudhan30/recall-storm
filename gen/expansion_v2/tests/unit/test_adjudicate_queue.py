"""Unit tests for recallstorm.adjudicate.queue."""
from contract import Verdict
from recallstorm.adjudicate.queue import (
    ReviewQueue,
    dequeue,
    enqueue,
    items_for_store,
    mark_reviewed,
    prioritize_items,
    queue_from_records,
    queue_size,
    queue_to_records,
)


def test_review_queue():
    q = ReviewQueue()
    enqueue(q, {"sku_id": "S1", "store_id": "WM1", "units": 10})
    enqueue(q, {"sku_id": "S2", "store_id": "WM1", "units": 30})
    assert queue_size(q) == 2
    assert len(items_for_store(q, "WM1")) == 2
    prio = prioritize_items(q.items)
    assert prio[0]["sku_id"] == "S2"
    mark_reviewed(q, "S1", "alice", Verdict.PULL)
    recs = queue_to_records(q)
    q2 = queue_from_records(recs)
    it, q2 = dequeue(q2)
    assert it is not None and it["verdict"] == "PULL"
    assert queue_size(q2) == 1
