"""Edge tests for recallstorm.adjudicate.queue."""
import pytest
from recallstorm.adjudicate.queue import (
    ReviewQueue,
    dequeue,
    enqueue,
    mark_reviewed,
)


def test_queue_edge():
    q = ReviewQueue()
    assert dequeue(q) is None
    with pytest.raises(ValueError):
        enqueue(q, {})
    with pytest.raises(ValueError):
        mark_reviewed(q, "S1", "BAD_VERDICT", "alice")
