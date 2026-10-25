"""Property tests for recallstorm.adjudicate.queue."""
from recallstorm.adjudicate.queue import ReviewQueue, dequeue, enqueue, queue_size


def test_queue_fifo_invariance():
    q = ReviewQueue()
    for i in range(15):
        enqueue(q, {"sku_id": f"S{i}"})
    assert queue_size(q) == 15
    for i in range(15):
        it, q = dequeue(q)
        assert it is not None and it["sku_id"] == f"S{i}"
    assert queue_size(q) == 0
