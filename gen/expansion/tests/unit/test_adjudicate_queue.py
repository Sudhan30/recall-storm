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
    enqueue(q, {"sku_id": "S1", "store_id": "WM1", "priority": 1})
    enqueue(q, {"sku_id": "S2", "store_id": "WM2", "priority": 5})
    assert queue_size(q) == 2
    assert len(items_for_store(q, "WM1")) == 1
    ordered = prioritize_items(q.items)
    assert ordered[0]["sku_id"] == "S2"
    assert mark_reviewed(q, "S1", Verdict.KEEP, "alice") is True
    assert queue_size(q) == 1
    recs = queue_to_records(q)
    q2 = queue_from_records(recs)
    assert len(q2.items) == 2
    popped = dequeue(q)
    assert popped is not None and popped["sku_id"] == "S2"
