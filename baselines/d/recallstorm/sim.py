"""OURS. Baseline D sim: turn scheduled shelf tasks into events.jsonl (MOVE, PULL|PLACE, DONE)."""
from __future__ import annotations

import json
from datetime import datetime

from ._src import src_of

SRC = src_of(__file__)
KIND = {"PULL": "PULL", "PLACE_SUB": "PLACE", "HOLD_VERIFY": None, "TAG_FLASH": None}


def events_for(tasks: list[dict]) -> list[dict]:
    ev = []
    for t in tasks:
        a, b = (datetime.fromisoformat(x) for x in t["window"])
        mid = a + (b - a) / 2
        base = {"store_id": t["store_id"], "associate_id": t["associate_id"], "loc": t["loc"], "task_id": t["task_id"]}
        ev.append({"t": a.isoformat(), **base, "kind": "MOVE"})
        if KIND.get(t["action"]):
            ev.append({"t": mid.isoformat(), **base, "kind": KIND[t["action"]]})
        ev.append({"t": b.isoformat(), **base, "kind": "DONE"})
    ev.sort(key=lambda e: (e["t"], e["store_id"], e["associate_id"] or "", e["task_id"]))
    return ev


def write_events(tasks: list[dict], path) -> int:
    ev = events_for(tasks)
    with open(path, "w") as fh:
        for e in ev:
            fh.write(json.dumps(e) + "\n")
    return len(ev)
