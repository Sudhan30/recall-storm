"""Edge case tests for recallstorm.adjudicate.queue."""
import pytest
from recallstorm.adjudicate.queue import ReviewQueue, dequeue, enqueue


def test_queue_edge():
    q = ReviewQueue()
    it, _ = dequeue(q)
    assert it is None
    with pytest.raises(ValueError):
        enqueue(q, {})
