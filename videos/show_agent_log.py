"""Print the managed-agent repair log (patches/agent/LOG.jsonl) one line per repair. Used for the video's terminal shot."""
import json, pathlib
for r in map(json.loads, (pathlib.Path(__file__).resolve().parent.parent / "patches/agent/LOG.jsonl").read_text().splitlines()):
    h = r.get("holdout") or {}
    ho = f"  held-out fixed {h['held_out_fixed']}/{h['held_out']}, new failures {len(h['new_failures'])}" if h.get("held_out") else ""
    print(f"{r['name']:<22} {r['result']:<10} {r['secs']:>6.1f} s  {r['before']['summary'].split(' in ')[0]:<22} -> "
          f"{r['after']['summary'].split(' in ')[0]}{ho}")
