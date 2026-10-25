"""Review queue management for HOLD_VERIFY items."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Verdict


@dataclass
class ReviewQueue:
    """FIFO / priority review queue for unclear labels."""

    items: list[dict] = field(default_factory=list)


def enqueue(queue: ReviewQueue, item: dict) -> ReviewQueue:
    """Add an item to the review queue."""
    if not isinstance(item, dict) or not item.get("sku_id"):
        raise ValueError("Queue item requires sku_id")
    queue.items.append(dict(item))
    return queue


def dequeue(queue: ReviewQueue) -> tuple[dict | None, ReviewQueue]:
    """Pop the first item from the review queue."""
    if not queue.items:
        return (None, queue)
    first = queue.items.pop(0)
    return (first, queue)


def queue_size(queue: ReviewQueue) -> int:
    """Return number of pending items in queue."""
    return len(queue.items)


def items_for_store(queue: ReviewQueue, store_id: str) -> list[dict]:
    """Return queue items linked to store_id."""
    return [it for it in queue.items if it.get("store_id") == store_id]


def prioritize_items(items: list[dict]) -> list[dict]:
    """Sort queue items by priority (higher units / earlier deadline first, then sku_id)."""
    return sorted(items, key=lambda x: (-int(x.get("units", 0)), str(x.get("sku_id", ""))))


def mark_reviewed(queue: ReviewQueue, sku_id: str, reviewer: str, verdict: Verdict) -> ReviewQueue:
    """Mark all items matching sku_id as reviewed with reviewer and resolved verdict."""
    for it in queue.items:
        if it.get("sku_id") == sku_id:
            it["reviewed"] = True
            it["reviewer"] = reviewer
            it["verdict"] = verdict.value
    return queue


def queue_to_records(queue: ReviewQueue) -> list[dict]:
    """Export queue items as serializable dictionary records."""
    return [{**it, "src": "recallstorm/adjudicate/queue.py"} for it in queue.items]


def queue_from_records(records: list[dict]) -> ReviewQueue:
    """Reconstruct a ReviewQueue from a list of dictionary records."""
    return ReviewQueue([dict(r) for r in records])
