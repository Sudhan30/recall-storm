"""ReviewQueue for managing HOLD_VERIFY items awaiting compliance inspection."""
from __future__ import annotations

from dataclasses import dataclass, field
from contract import Verdict


@dataclass
class ReviewQueue:
    """FIFO / priority queue of HOLD_VERIFY items."""

    items: list[dict] = field(default_factory=list)


def enqueue(queue: ReviewQueue, item: dict) -> None:
    """Add an item to the review queue."""
    if not isinstance(queue, ReviewQueue):
        raise TypeError("queue must be a ReviewQueue")
    if not isinstance(item, dict) or not item.get("sku_id"):
        raise ValueError("Queue item must be a dict with sku_id")
    entry = {
        "sku_id": str(item["sku_id"]),
        "store_id": item.get("store_id"),
        "priority": int(item.get("priority", 1)),
        "reason": str(item.get("reason", "HOLD_VERIFY")),
        "reviewed": bool(item.get("reviewed", False)),
        "verdict": item.get("verdict", Verdict.HOLD_VERIFY.value),
        "reviewer": item.get("reviewer"),
    }
    queue.items.append(entry)


def dequeue(queue: ReviewQueue) -> dict | None:
    """Pop and return the first unreviewed item in the queue, or None."""
    if not isinstance(queue, ReviewQueue):
        raise TypeError("queue must be a ReviewQueue")
    for idx, it in enumerate(queue.items):
        if not it.get("reviewed", False):
            return queue.items.pop(idx)
    return None


def queue_size(queue: ReviewQueue) -> int:
    """Return count of unreviewed items in the queue."""
    if not isinstance(queue, ReviewQueue):
        raise TypeError("queue must be a ReviewQueue")
    return sum(1 for it in queue.items if not it.get("reviewed", False))


def items_for_store(queue: ReviewQueue, store_id: str) -> list[dict]:
    """Return queue items belonging to store_id."""
    return [it for it in queue.items if it.get("store_id") == store_id]


def prioritize_items(items: list[dict]) -> list[dict]:
    """Sort queue items by descending priority then ascending sku_id."""
    return sorted(items, key=lambda it: (-int(it.get("priority", 1)), str(it.get("sku_id", ""))))


def mark_reviewed(queue: ReviewQueue, sku_id: str, verdict: Verdict | str, reviewer: str) -> bool:
    """Mark a queued item as reviewed with a final verdict."""
    v = verdict.value if isinstance(verdict, Verdict) else str(verdict)
    if v not in {x.value for x in Verdict}:
        raise ValueError(f"Invalid verdict: {v}")
    found = False
    for it in queue.items:
        if it.get("sku_id") == sku_id:
            it["reviewed"] = True
            it["verdict"] = v
            it["reviewer"] = reviewer
            found = True
    return found


def queue_to_records(queue: ReviewQueue) -> list[dict]:
    """Export all items in the queue as plain dicts."""
    return [dict(it) for it in queue.items]


def queue_from_records(records: list[dict]) -> ReviewQueue:
    """Reconstruct a ReviewQueue from a list of record dicts."""
    q = ReviewQueue()
    for r in records:
        enqueue(q, r)
    return q
