"""Print the managed-agent repair log (patches/agent/LOG.jsonl) for the video's terminal shot.

One line per finished repair (a re-graded entry replaces its original). For repairs on the 20-store drill it adds
plan mistakes before -> after and the held-out (unseen) stores' mistakes, then the result of both expansion
patches together from reports/expansion_agentpatched_plan.json.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = {}
for r in map(json.loads, (ROOT / "patches/agent/LOG.jsonl").read_text().splitlines()):
    if r.get("status") == "completed":
        rows[r["name"].removesuffix("_regraded")] = r
for name, r in rows.items():
    db, da, dh = r.get("drill_before") or {}, r.get("drill_after") or {}, r.get("drill_holdout") or {}
    extra = ""
    if db and da and all(str(s).startswith(("WM", "SAMS")) for s in dh.get("held_stores", [])):
        extra = (f"  plan mistakes {db['hard']:,} -> {da['hard']:,}; "
                 f"{len(dh['held_stores'])} unseen stores {dh['held_before']:,} -> {dh['held_after']:,}")
    print(f"{name:<28} {r['result']:<10} {r['secs']:>6.1f} s{extra}")
p = ROOT / "reports/expansion_agentpatched_plan.json"
if p.exists():
    print(f"both expansion patches together ({p.relative_to(ROOT)}): plan mistakes {json.loads(p.read_text())['hard_errors']:,}")
