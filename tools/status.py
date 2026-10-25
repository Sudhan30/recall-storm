"""OURS. Writes viewer/data/status.json every 10 s for viewer/status.html (live build status).

Usage: python tools/status.py [--once]
"""
import json, pathlib, re, subprocess, sys, time
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "viewer" / "data" / "status.json"
RUNS = ["expansion_v2", "expansion", "probe", "core", "b_rules", "b_allocate", "b_route"]
TARGETS = {"expansion_v2": 665_000, "expansion": 254_377}   # v2: G3b projection (242 tok/fn measured); v1: final
DEADLINES = [("G3a first v2 seam", "12:01"), ("G3b v2 health", "12:15"), ("Core demo frozen + backup video", "13:30"),
             ("G4 hard stop", "14:45"), ("G5 numbers frozen", "15:30"), ("Push + README", "16:15"), ("Submit", "16:50")]


def jl(p: pathlib.Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def last_line(p: pathlib.Path) -> dict | None:
    if not p.exists() or p.stat().st_size == 0:
        return None
    with open(p, "rb") as f:
        f.seek(max(0, p.stat().st_size - 4096))
        for line in reversed(f.read().decode(errors="replace").splitlines()):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def alive(pattern: str) -> bool:
    return subprocess.run(["pgrep", "-f", pattern], capture_output=True).returncode == 0


def run_status(name: str) -> dict | None:
    d = ROOT / "runs" / name
    if not d.exists():
        return None
    hops = [h for h in jl(d / "hops.jsonl") if "finish" in h]
    last = last_line(d / "stream_log.jsonl")
    done_vis = sum(h.get("visible_hop") or 0 for h in hops)
    running = alive(f"argon_run.py {name} ")
    live_vis = done_vis + ((last or {}).get("visible_hop") or 0 if running and last and last.get("hop") == len(hops) else 0)
    t = (last or {}).get("t") or (hops[-1]["t"] if hops else 0)
    rate = live_vis / t if t else 0
    target = TARGETS.get(name)
    eta = None
    if running and rate and target and live_vis < target:
        eta = time.strftime("%H:%M", time.localtime(time.time() + (target - live_vis) / rate))
    stream = d / "stream.txt"
    files = 0
    manifest = 0
    if stream.exists():
        txt = stream.read_text(errors="replace")
        files = txt.count("<<<END FILE>>>")
        m = re.search(r"<<<MANIFEST>>>(.*?)<<<END MANIFEST>>>", txt, re.S)
        manifest = sum(1 for l in (m.group(1) if m else "").splitlines() if l.strip().startswith("{"))
    seams = None
    rep = ROOT / "reports" / f"{name}_seams.json"
    if hops and len(hops) > 1 or (hops and hops[-1].get("finish") == "CONTINUATION"):
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "seam_check.py"), str(d)], capture_output=True, text=True)
        m = re.search(r"(\d+) PASS, (\d+) FAIL, (\d+) PENDING", r.stdout)
        if m:
            seams = {"pass": int(m[1]), "fail": int(m[2]), "pending": int(m[3])}
    return {"name": name, "running": running, "hops": len(hops), "visible": live_vis, "secs": round(t),
            "rate": round(rate), "target": target, "eta": eta, "files": files, "manifest": manifest,
            "finish": hops[-1]["finish"] if hops else None, "seams": seams,
            "input_tokens": sum(h.get("prompt_hop") or 0 for h in hops)}


def plan_summary(name: str) -> dict | None:
    p = ROOT / "reports" / f"{name}_plan.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    c = r.get("classification") or {}
    return {"name": name, "hard": r.get("hard_errors"), "by_check": r.get("by_check"),
            "precision": c.get("pull_precision") or c.get("precision"), "recall": c.get("pull_recall") or c.get("recall")}


def snapshot() -> dict:
    git = subprocess.run(["git", "log", "--format=%h|%cr|%s", "-8"], capture_output=True, text=True, cwd=ROOT).stdout
    unpushed = subprocess.run(["git", "rev-list", "--count", "origin/main..HEAD"], capture_output=True, text=True,
                              cwd=ROOT).stdout.strip()
    repairs = [{k: e.get(k) for k in ("name", "result", "secs", "diagnosis", "before", "after", "holdout", "drill_holdout")}
               for e in jl(ROOT / "patches" / "agent" / "LOG.jsonl")]
    vids = sorted(p.name for p in (ROOT / "videos").glob("*.mp4")) if (ROOT / "videos").exists() else []
    lots = sorted(p.name for p in (ROOT / "reports").glob("*_lots.json"))
    now = datetime.now().strftime("%H:%M")
    return {
        "updated": datetime.now().strftime("%H:%M:%S"),
        "runs": [r for r in (run_status(n) for n in RUNS) if r],
        "plans": [p for p in (plan_summary(n) for n in ["core", "core_patched", "expansion", "baseline_d", "baseline_c",
                                                         "expansion_v2"]) if p],
        "repairs": repairs, "repair_running": alive("repair_agent.py"),
        "videos": vids, "lots_reports": lots,
        "fda_lots_started": (ROOT / "data" / "build_fda_lots.py").exists(),
        "deadlines": [{"label": l, "at": t, "past": now >= t} for l, t in DEADLINES],
        "git": [dict(zip(("hash", "when", "msg"), l.split("|", 2))) for l in git.splitlines()],
        "unpushed": int(unpushed or 0),
    }


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    while True:
        tmp = OUT.with_suffix(".tmp")
        tmp.write_text(json.dumps(snapshot(), indent=1))
        tmp.replace(OUT)
        if "--once" in sys.argv:
            break
        time.sleep(10)
