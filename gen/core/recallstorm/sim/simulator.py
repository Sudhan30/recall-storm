"""Replay planned shelf tasks into chronological associate events with walking time."""
from __future__ import annotations

from datetime import datetime, timedelta
import json
from pathlib import Path
import re
from typing import Any

from contract import Action


def _aisle_num(aisle: str) -> int:
    m = re.search(r"\d+", str(aisle))
    return int(m.group(0)) if m else 0


def _walking_seconds(loc_a: dict[str, Any] | None, loc_b: dict[str, Any]) -> int:
    """Compute realistic walking time in seconds between two shelf locations."""
    if loc_a is None:
        return 15
    if loc_a == loc_b:
        return 2
    aisle_diff = abs(_aisle_num(loc_a["aisle"]) - _aisle_num(loc_b["aisle"]))
    bay_diff = abs(int(loc_a["bay"]) - int(loc_b["bay"]))
    shelf_diff = abs(int(loc_a["shelf"]) - int(loc_b["shelf"]))
    secs = 5 + aisle_diff * 12 + bay_diff * 3 + shelf_diff * 1
    return min(max(secs, 3), 60)


def simulate_events(plan_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replay shelf_task records into MOVE, PULL, PLACE, and DONE events."""
    tasks = [r for r in plan_records if r.get("type") == "shelf_task"]

    # Group tasks by (store_id, associate_id) ordered by seq
    by_assoc: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for t in tasks:
        key = (str(t["store_id"]), str(t["associate_id"]))
        by_assoc.setdefault(key, []).append(t)

    events: list[dict[str, Any]] = []

    for (store_id, assoc_id), assoc_tasks in sorted(by_assoc.items()):
        assoc_tasks.sort(key=lambda x: (int(x["seq"]), x["window"][0], x["task_id"]))
        prev_loc: dict[str, Any] | None = None
        cursor: datetime | None = None

        for t in assoc_tasks:
            w_start = datetime.fromisoformat(t["window"][0])
            w_end = datetime.fromisoformat(t["window"][1])
            loc = t["loc"]
            task_id = t["task_id"]
            action = t["action"]

            if cursor is None or cursor < w_start:
                cursor = w_start

            walk_secs = _walking_seconds(prev_loc, loc)
            move_time = cursor
            work_time = move_time + timedelta(seconds=walk_secs)
            done_time = work_time + timedelta(seconds=max(10, int(t.get("qty_units", 1)) * 2))

            # Clamp timestamps inside [w_start, w_end]
            if done_time > w_end:
                done_time = w_end
                work_time = max(move_time + timedelta(seconds=1), done_time - timedelta(seconds=5))
                if work_time <= move_time:
                    move_time = w_start
                    work_time = w_start + (w_end - w_start) / 2

            # 1. MOVE event
            events.append(
                {
                    "t": move_time.isoformat(),
                    "store_id": store_id,
                    "associate_id": assoc_id,
                    "kind": "MOVE",
                    "loc": loc,
                    "task_id": task_id,
                }
            )

            # 2. Action event (PULL or PLACE)
            event_kind = (
                "PLACE"
                if action in (Action.PLACE_SUB.value, Action.TAG_FLASH.value)
                else "PULL"
            )
            events.append(
                {
                    "t": work_time.isoformat(),
                    "store_id": store_id,
                    "associate_id": assoc_id,
                    "kind": event_kind,
                    "loc": loc,
                    "task_id": task_id,
                }
            )

            # 3. DONE event
            events.append(
                {
                    "t": done_time.isoformat(),
                    "store_id": store_id,
                    "associate_id": assoc_id,
                    "kind": "DONE",
                    "loc": loc,
                    "task_id": task_id,
                }
            )

            prev_loc = loc
            cursor = done_time + timedelta(seconds=1)

    events.sort(key=lambda e: (e["t"], e["store_id"], e["associate_id"], e["task_id"]))
    return events


def write_events_jsonl(events: list[dict[str, Any]], out_path: str | Path) -> None:
    """Write simulated events to a JSONL file."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, separators=(",", ":")) + "\n")
