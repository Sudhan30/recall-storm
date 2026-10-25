"""OURS. Builds viewer/data/compare.json for viewer/compare.html: per-associate task timelines for two drills.

An overlap is a task that starts before the associate's previous task ends: verify_plan's labor rule.
Usage: python viewer/build_compare.py [LEFT RIGHT]   (defaults: expansion expansion_agentpatched)
"""
import json, pathlib, sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEFT, RIGHT = (sys.argv[1:3] if len(sys.argv) >= 3 else ["expansion", "expansion_agentpatched"])
LABELS = {"expansion": "Expansion v1 — Argon's code, unedited",
          "expansion_agentpatched": "Expansion v1 + managed-agent fixes",
          "core": "Core — Argon's first draft", "core_patched": "Core + 3 small fixes"}


def load(name: str) -> dict:
    by_store: dict[str, dict[str, list]] = {}
    for line in open(ROOT / "out" / name / "plan.jsonl"):
        if '"shelf_task"' not in line:
            continue
        t = json.loads(line)
        w = t.get("window") or []
        if len(w) != 2 or not t.get("associate_id"):
            continue
        s, e = datetime.fromisoformat(w[0]).timestamp(), datetime.fromisoformat(w[1]).timestamp()
        by_store.setdefault(t["store_id"], {}).setdefault(t["associate_id"], []).append(
            [s, e, t["action"], t.get("sku_id"), t["task_id"]])
    out = {}
    for sid, assoc in by_store.items():
        rows, overlaps = [], 0
        for aid, tasks in sorted(assoc.items()):
            tasks.sort()
            bad = set()
            for i in range(1, len(tasks)):              # same rule as verify_plan: each task vs the one before it
                if tasks[i][0] < tasks[i - 1][1]:
                    bad.update((i - 1, i)); overlaps += 1
            rows.append({"id": aid, "tasks": [[*t[:3], i in bad] for i, t in enumerate(tasks)]})
        out[sid] = {"rows": rows, "overlaps": overlaps, "tasks": sum(len(r["tasks"]) for r in rows)}
    return out


left, right = load(LEFT), load(RIGHT)
stores = sorted(set(left) & set(right), key=lambda s: -left[s]["overlaps"])
starts = [t[0] for d in (left, right) for s in d.values() for r in s["rows"] for t in r["tasks"]]
ends = [t[1] for d in (left, right) for s in d.values() for r in s["rows"] for t in r["tasks"]]
data = {"left": {"name": LEFT, "label": LABELS.get(LEFT, LEFT), "stores": {s: left[s] for s in stores},
                 "overlaps": sum(v["overlaps"] for v in left.values())},
        "right": {"name": RIGHT, "label": LABELS.get(RIGHT, RIGHT), "stores": {s: right[s] for s in stores},
                  "overlaps": sum(v["overlaps"] for v in right.values())},
        "stores": stores, "t0": min(starts), "t1": max(ends),
        "deadline": datetime.fromisoformat("2027-01-01T00:00:00-08:00").timestamp()}
(ROOT / "viewer" / "data").mkdir(exist_ok=True)
(ROOT / "viewer" / "data" / "compare.json").write_text(json.dumps(data, separators=(",", ":")))
print(f"stores {len(stores)} | {LEFT} overlaps {data['left']['overlaps']} | {RIGHT} overlaps {data['right']['overlaps']} | "
      f"worst store {stores[0]} ({left[stores[0]]['overlaps']} vs {right[stores[0]]['overlaps']})")
