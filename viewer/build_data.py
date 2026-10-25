"""OURS (P4). Copy/derive the JSON the viewer reads into viewer/data/live/ from real artifacts.

Usage (repo root):  python3 viewer/build_data.py          # one shot
                    python3 viewer/build_data.py --watch  # rebuild every 20 s during the day

Reads whatever exists (every source is optional):
  data/stores.jsonl, facings.jsonl, skus.jsonl            -> map + 3D store geometry
  out/<name>/plan.jsonl, events.jsonl                     -> drill_<name>.json   (map, 3D store, evidence)
  runs/<name>/hops.jsonl + stream_log.jsonl + stream.txt  -> run_<name>.json     (hops & seams)
  runs/<name>/events.jsonl (argon_bg)                     -> run_<name>.json
  reports/<name>_seams.json                               -> seam PASS/FAIL in run_<name>.json
  gen/<name>/offsets.jsonl (+ manifest.jsonl, files)      -> code_<name>.json + src/<name>/... copies
  reports/<name>_code.json, deps.jsonl                    -> statuses, edges, failures in code_<name>.json
  reports/<name>_plan.json                                -> verify.json
Anything missing is skipped; the viewer then falls back to viewer/data/fixture/ with a FIXTURE badge.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = ROOT / "viewer" / "data" / "live"
PRICE_OUT, PRICE_IN = 10 / 1e6, 2 / 1e6
BUCKETS = [(0, 200_000), (200_000, 400_000), (400_000, 600_000), (600_000, 10**12)]
FALLBACK_PLAN_TYPES = {
    "run": ("run_id", "scenario_id", "generator", "as_of", "rule_ids", "src"),
    "sku_verdict": ("sku_id", "gtin", "verdict", "additive", "match", "rule_ids", "jurisdictions",
                    "decided_by", "evidence_id", "src"),
    "evidence": ("evidence_id", "sku_id", "rule_id", "clause_ref", "source_span", "rationale", "src"),
    "store_playbook": ("store_id", "format", "deadline", "windows", "counts", "associate_ids",
                       "exception_ids", "manifest_ids", "src"),
    "shelf_task": ("task_id", "store_id", "sku_id", "action", "loc", "qty_units", "associate_id",
                   "window", "seq", "evidence_id", "sub_sku_id", "alloc_id", "src"),
    "exception": ("exc_id", "store_id", "kind", "note_id", "resolution", "task_ids", "src"),
    "allocation": ("alloc_id", "dc_id", "sub_sku_id", "store_id", "qty_cases", "dc_balance_after", "src"),
    "handoff": ("handoff_id", "kind", "from_id", "to_id", "window", "qty", "ref_ids", "src"),
    "route_manifest": ("manifest_id", "truck_id", "dc_id", "stops", "limits", "depart", "src"),
}


# ------------------------------------------------------------------ helpers
def jl(p: pathlib.Path) -> list[dict]:
    if not p or not p.exists():
        return []
    rows = []
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                v = json.loads(line)
                if isinstance(v, dict):
                    rows.append(v)
            except json.JSONDecodeError:
                continue                     # partial last line of a live log
    return rows


def jload(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None


SIG = hashlib.sha1()
FILE_SIGS: dict[str, str] = {}


def dump(name: str, obj) -> None:
    LIVE.mkdir(parents=True, exist_ok=True)
    tmp = LIVE / (name + ".tmp")
    txt = json.dumps(obj, separators=(",", ":"), default=str)
    if name != "index.json":
        SIG.update(name.encode() + txt.encode())
        FILE_SIGS[name] = hashlib.sha1(txt.encode()).hexdigest()[:12]
    tmp.write_text(txt, encoding="utf-8")
    tmp.replace(LIVE / name)


def plan_types() -> dict:
    try:
        tree = ast.parse((ROOT / "contract.py").read_text())
        for node in tree.body:
            tgt = node.target if isinstance(node, ast.AnnAssign) else (node.targets[0] if isinstance(node, ast.Assign) else None)
            if isinstance(tgt, ast.Name) and tgt.id == "PLAN_TYPES" and node.value is not None:
                return {k: tuple(v) for k, v in ast.literal_eval(node.value).items()}
    except Exception:
        pass
    return FALLBACK_PLAN_TYPES


def bucket_of(tok) -> int | None:
    if tok is None:
        return None
    for i, (a, b) in enumerate(BUCKETS):
        if a <= tok < b:
            return i
    return None


def downsample(points: list, n: int = 2500) -> list:
    if len(points) <= n:
        return points
    step = len(points) / n
    out = [points[int(i * step)] for i in range(n)]
    out.append(points[-1])
    return out


# ------------------------------------------------------------------ drills
def classify(rec: dict, types: dict) -> str | None:
    for k in ("type", "record_type", "record", "kind", "_type"):
        v = rec.get(k)
        if isinstance(v, str) and v in types:
            return v
    best, score = None, 0.0
    keys = set(rec)
    for t, fields in types.items():
        s = len(keys & set(fields)) / len(fields)
        if s > score:
            best, score = t, s
    return best if score >= 0.6 else None


def build_drills(index: dict) -> None:
    stores = jl(ROOT / "data" / "stores.jsonl")
    facings = jl(ROOT / "data" / "facings.jsonl")
    skus = {s["sku_id"]: s for s in jl(ROOT / "data" / "skus.jsonl") if "sku_id" in s}
    types = plan_types()
    out = ROOT / "out"
    if not out.is_dir():
        return
    for d in sorted(p for p in out.iterdir() if p.is_dir()):
        ev_p, plan_p = d / "events.jsonl", d / "plan.jsonl"
        if not ev_p.exists() and not plan_p.exists():
            continue
        plan: dict[str, list] = {t: [] for t in types}
        plan["_unknown"] = []
        for r in jl(plan_p):
            t = classify(r, types)
            plan[t or "_unknown"].append(r)
        events = jl(ev_p)
        events.sort(key=lambda e: str(e.get("t")))
        sids = {e.get("store_id") for e in events} | {t.get("store_id") for t in plan["shelf_task"]}
        st = stores or [{"store_id": s, "lat": None, "lon": None} for s in sorted(x for x in sids if x)]
        used = {f.get("sku_id") for f in facings} | {v.get("sku_id") for v in plan["sku_verdict"]}
        obj = {"name": d.name, "fixture": False,
               "source": {"stores": "data/stores.jsonl", "events": f"out/{d.name}/events.jsonl",
                          "plan": f"out/{d.name}/plan.jsonl"},
               "stores": st, "facings": facings, "rules": jl(ROOT / "data" / "rules.jsonl"),
               "skus": {k: {"name": v.get("name"), "brand": v.get("brand"), "category": v.get("category"),
                            "ingredients": v.get("ingredients", "")} for k, v in skus.items() if k in used},
               "plan": {k: v for k, v in plan.items() if k in ("sku_verdict", "evidence", "shelf_task",
                                                               "store_playbook", "exception", "_unknown")},
               "counts": {k: len(v) for k, v in plan.items()},
               "events": events}
        dump(f"drill_{d.name}.json", obj)
        index["drills"].append(d.name)


# ------------------------------------------------------------------ runs (hops & seams)
def snippet(data: bytes, byte: int | None, w: int = 220) -> tuple[str, str]:
    if byte is None or not data:
        return "", ""
    return (data[max(0, byte - w):byte].decode("utf-8", errors="replace"),
            data[byte:byte + w].decode("utf-8", errors="replace"))


def run_from_hops(name: str, rd: pathlib.Path) -> dict | None:
    log, hops = jl(rd / "stream_log.jsonl"), jl(rd / "hops.jsonl")
    if not log and not hops:
        return None
    fin = [h for h in hops if "finish" in h]
    fin_by = {h["hop"]: h for h in fin}
    base: dict[int, int] = {}

    def b(h: int) -> int:
        if h <= 0:
            return 0
        if h not in base:
            prev = fin_by.get(h - 1)
            base[h] = int(prev["visible_total"]) if prev and prev.get("visible_total") is not None else b(h - 1)
        return base[h]

    think_base: dict[int, int] = {}

    def tb(h: int) -> int:
        if h <= 0:
            return 0
        if h not in think_base:
            prev = fin_by.get(h - 1)
            think_base[h] = tb(h - 1) + int((prev or {}).get("thinking_hop") or 0)
        return think_base[h]

    points = [[0, 0, 0]]
    for r in log:
        if r.get("visible_hop") is None:
            continue
        h = int(r.get("hop", 0))
        points.append([r.get("t", 0), b(h) + int(r["visible_hop"]), tb(h) + int(r.get("thinking_hop") or 0)])
    for h in fin:                                       # make sure every hop end is on the curve
        points.append([h.get("t", 0), h.get("visible_total") or 0, tb(h["hop"]) + int(h.get("thinking_hop") or 0)])
    points.sort(key=lambda p: (p[0], p[1]))
    data = (rd / "stream.txt").read_bytes() if (rd / "stream.txt").exists() else b""
    rep = jload(ROOT / "reports" / f"{name}_seams.json") or {}
    rep_by_byte = {s.get("seam_byte"): s for s in rep.get("seams", []) if isinstance(s, dict)}
    seams = []
    for h in fin:
        if h.get("finish") == "CONTINUATION":
            sb = h.get("seam_byte")
            r = rep_by_byte.get(sb, {})
            be, af = snippet(data, sb)
            seams.append({"n": len(seams) + 1, "hop": h["hop"], "t": h.get("t"), "tok": h.get("visible_total"),
                          "seam_byte": sb, "has_token": h.get("has_token"),
                          "status": r.get("status", "UNCHECKED"), "fails": r.get("fails", []),
                          "notes": r.get("notes", []), "before": be, "after": af})
    resumes = [h for h in hops if "resume" in h or "error" in h]
    last_t = max([p[0] for p in points] + [h.get("t", 0) or 0 for h in hops] + [0])
    n_hops = max([int(r.get("hop", 0)) for r in log + hops] + [0]) + 1
    live = not fin or fin[-1].get("finish") == "CONTINUATION" or (log and int(log[-1].get("hop", 0)) > fin[-1]["hop"])
    visible = max(p[1] for p in points)
    thinking = max(p[2] for p in points)
    prompt_known = [int(h.get("prompt_hop") or 0) for h in fin]
    prompt = sum(prompt_known)
    if live and prompt_known:                      # the live hop has re-read the prompt too
        prompt += prompt_known[-1]
    cost = (visible + thinking) * PRICE_OUT + prompt * PRICE_IN
    return {"name": name, "fixture": False, "kind": "run", "points": downsample(points),
            "hops": fin, "resumes": resumes, "seams": seams,
            "summary": {"visible": visible, "thinking": thinking, "prompt": prompt, "hops": n_hops,
                        "minutes": round(last_t / 60, 1), "cost_usd": round(cost, 2), "live": bool(live),
                        "seams_pass": sum(s["status"] == "PASS" for s in seams),
                        "seams_fail": sum(s["status"] == "FAIL" for s in seams),
                        "stream_bytes": len(data)}}


def run_from_bg(name: str, rd: pathlib.Path) -> dict | None:
    ev = jl(rd / "events.jsonl")
    if not ev:
        return None
    data = (rd / "stream.txt").read_bytes() if (rd / "stream.txt").exists() else b""
    rep = jload(ROOT / "reports" / f"{name}_seams.json") or {}
    rep_by_byte = {s.get("seam_byte"): s for s in rep.get("seams", []) if isinstance(s, dict)}
    anchors = []                                      # (bytes, visible) from status updates with usage
    last_usage = None
    for e in ev:
        u = e.get("usage")
        if e.get("type") == "interaction.status_update" and isinstance(u, dict):
            vis = int(u.get("total_output_tokens") or 0) - int(u.get("total_thought_tokens") or 0)
            anchors.append((e.get("seam_byte") or 0, vis, e))
            last_usage = u
    bpt = (anchors[-1][0] / anchors[-1][1]) if anchors and anchors[-1][1] else 3.4
    points, est = [[0, 0, 0]], False
    for e in ev:
        if e.get("type") == "step.delta" and e.get("out_bytes"):
            points.append([e.get("t", 0), int(e["out_bytes"] / bpt), None]); est = True
        elif e.get("type") == "interaction.status_update" and isinstance(e.get("usage"), dict):
            u = e["usage"]
            points.append([e.get("t", 0), int(u.get("total_output_tokens") or 0) - int(u.get("total_thought_tokens") or 0),
                           int(u.get("total_thought_tokens") or 0)])
    for p in points:
        if p[2] is None:
            p[2] = 0
    seams, hops = [], []
    for byte, vis, e in anchors:
        hops.append({"hop": len(hops), "t": e.get("t"), "visible_total": vis, "seam_byte": byte,
                     "status": e.get("status"), "has_token": e.get("has_token")})
        if e.get("has_token"):
            r = rep_by_byte.get(byte, {})
            be, af = snippet(data, byte)
            seams.append({"n": len(seams) + 1, "hop": len(seams), "t": e.get("t"), "tok": vis, "seam_byte": byte,
                          "has_token": True, "status": r.get("status", "UNCHECKED"), "fails": r.get("fails", []),
                          "notes": r.get("notes", []), "before": be, "after": af})
    u = last_usage or {}
    out_t = int(u.get("total_output_tokens") or 0)
    thought = int(u.get("total_thought_tokens") or 0)
    inp = int(u.get("total_input_tokens") or 0)
    done = any(e.get("type") == "interaction.completed" for e in ev)
    last_t = max([e.get("t", 0) or 0 for e in ev] + [0])
    return {"name": name, "fixture": False, "kind": "bg", "points": downsample(points), "hops": hops,
            "resumes": [e for e in ev if "reconnect" in e], "seams": seams, "tokens_estimated_from_bytes": est,
            "summary": {"visible": max(out_t - thought, max(p[1] for p in points)), "thinking": thought,
                        "prompt": inp, "hops": len(seams) + 1, "minutes": round(last_t / 60, 1),
                        # background usage: output total treated as incl. thinking (BUILD.md sec 13)
                        "cost_usd": round(out_t * PRICE_OUT + inp * PRICE_IN, 2), "live": not done,
                        "seams_pass": sum(s["status"] == "PASS" for s in seams),
                        "seams_fail": sum(s["status"] == "FAIL" for s in seams), "stream_bytes": len(data)}}


def build_runs(index: dict) -> None:
    runs = ROOT / "runs"
    if not runs.is_dir():
        return
    for rd in sorted(p for p in runs.iterdir() if p.is_dir()):
        try:
            if (rd / "hops.jsonl").exists() or (rd / "stream_log.jsonl").exists():
                obj = run_from_hops(rd.name, rd)
            else:
                obj = run_from_bg(rd.name, rd)
        except Exception as e:                       # a half-written log must never kill the build
            print(f"  run {rd.name}: skipped ({e!r})", file=sys.stderr); continue
        if obj and (obj["summary"]["visible"] or obj["hops"]):
            dump(f"run_{rd.name}.json", obj)
            index["runs"].append(rd.name)


# ------------------------------------------------------------------ code wall
FAILISH = re.compile(r"fail|error|broken|missing|unresolved|stub|dup|mismatch|bad", re.I)


def walk_failures(node, check=None, out=None):
    """Find dicts that look like a per-file problem anywhere inside a verifier report."""
    if out is None:
        out = []
    if isinstance(node, dict):
        path = node.get("path") or node.get("file") or node.get("src") or node.get("use_path")
        bad = (node.get("ok") is False or node.get("passed") is False or
               (isinstance(node.get("status"), str) and FAILISH.search(node["status"])) or
               (("message" in node or "error" in node or "msg" in node or "reason" in node) and
                node.get("ok") is not True and node.get("status") not in ("pass", "PASS", "ok", "OK")))
        if isinstance(path, str) and bad:
            out.append({"check": node.get("check") or check or "?", "path": path,
                        "line": node.get("line") or node.get("lineno") or node.get("use_line"),
                        "message": str(node.get("message") or node.get("error") or node.get("msg") or
                                       node.get("reason") or node.get("status") or "")[:400],
                        "severity": node.get("severity")})
        for k, v in node.items():
            ck = k if re.fullmatch(r"D\d+[a-z]?", str(k)) else check
            if isinstance(v, (dict, list)):
                walk_failures(v, ck, out)
    elif isinstance(node, list):
        for v in node:
            walk_failures(v, check, out)
    return out


def per_file_status(rep) -> dict:
    out = {}
    files = rep.get("files") if isinstance(rep, dict) else None
    items = files.items() if isinstance(files, dict) else ((f.get("path"), f) for f in files or [] if isinstance(f, dict))
    for p, v in items:
        if not p:
            continue
        if isinstance(v, str):
            out[p] = v
        elif isinstance(v, dict):
            s = v.get("status")
            if s is None and "ok" in v:
                s = "pass" if v["ok"] else "fail"
            if s is None and "passed" in v:
                s = "pass" if v["passed"] else "fail"
            if s is not None:
                out[p] = str(s)
    return out


def norm_status(s: str | None) -> str:
    if not s:
        return "unknown"
    s = s.lower()
    if s in ("pass", "ok", "passed", "green"):
        return "pass"
    if "warn" in s or "stub" in s or "dup" in s:
        return "warn"
    if FAILISH.search(s):
        return "fail"
    return "unknown"


OK_D1 = ("ok", "ok_nonpy", "ok_reexport_opaque")
BAD_D4 = ("collection_error", "timeout", "failed", "error", "checker_error")


def failures_verify_code(rep: dict) -> list[dict]:
    """tools/verify_code.py report (keys totals, d1, d2, d3, d4, d6, parse_errors) -> flat failure list."""
    out = []

    def add(check, path, line, msg, tok, sev):
        if path:
            out.append({"check": check, "path": path, "line": line, "message": str(msg)[:400], "tok": tok, "severity": sev})
    for e in rep.get("parse_errors") or []:
        add("parse", e.get("path"), e.get("line"), f"parse error: {e.get('msg') or e.get('error') or e}", e.get("tok"), 9)
    d1 = rep.get("d1") or {}
    for r in d1.get("files") or []:
        if r.get("status") not in OK_D1:
            add("D1", r.get("path"), None, f"manifest file: {r.get('status')}", r.get("tok"), 7)
    for r in d1.get("symbols") or []:
        if r.get("status") not in OK_D1:
            add("D1", r.get("path"), r.get("line"), f"promised {r.get('promise')}: {r.get('status')}"
                + (f" ({r['detail']})" if r.get("detail") else ""), r.get("tok"), 6)
    d2 = rep.get("d2") or {}
    for r in (d2.get("edges_bad") or []) + (d2.get("calls_bad") or []):
        add("D2", r.get("from_path") or r.get("path"), r.get("line") or r.get("_line"),
            f"{r.get('symbol') or ''} from {r.get('to_path') or '?'}: {r.get('status')}"
            + (f" ({r['detail']})" if r.get("detail") else ""), r.get("use_tok") or r.get("tok"), 8)
    for r in rep.get("d3") or []:
        add("D3", r.get("path"), r.get("line"), f"literal '{r.get('literal')}' not in contract enums"
            + (" (test file)" if r.get("is_test") else ""), r.get("tok"), 1 if r.get("is_test") else 4)
    for r in rep.get("d4") or []:
        if r.get("status") in BAD_D4 or r.get("failed") or r.get("errors"):
            bad = [c for c in r.get("cases") or [] if c.get("outcome") not in ("passed", "skipped")]
            if not bad:
                add("D4", r.get("path"), None, f"pytest {r.get('status')}: {r.get('detail') or r.get('msg') or ''}"
                    f" ({r.get('passed', 0)}/{r.get('tests', 0)} passed)", r.get("tok"), 7)
            for c in bad[:4]:
                add("D4", r.get("path"), c.get("line"), f"{c.get('name')}: {c.get('outcome')} {c.get('msg') or ''}",
                    c.get("tok") or r.get("tok"), 7)
    d6 = rep.get("d6") or {}
    for r in d6.get("stubs") or []:
        add("D6", r.get("path"), r.get("line"), f"stub {r.get('kind') or ''} {r.get('name') or ''}", r.get("tok"), 5)
    for r in d6.get("placeholders") or []:
        add("D6", r.get("path"), r.get("line"), f"placeholder: {r.get('text') or ''}", r.get("tok"), 5)
    for g in d6.get("dup_examples") or []:
        locs = g.get("locations") or []
        if len(locs) >= 2:
            a, b = locs[0], locs[1]
            add("D6", b.get("path"), b.get("start"), f"8-line window duplicated ({g.get('count')}x), first at "
                f"{a.get('path')}:{a.get('start')}", b.get("tok"), 2)
    for g in d6.get("near_duplicate_tests") or []:
        m = g.get("members") or []
        if m:
            first = m[0] if isinstance(m[0], dict) else {"path": str(m[0])}
            add("D6", first.get("path"), first.get("line"), f"{g.get('count')} near-duplicate test bodies", first.get("tok"), 2)
    for e in rep.get("errors") or []:
        if isinstance(e, dict):
            add("checker", e.get("path"), e.get("line"), e.get("detail") or e.get("error") or e, e.get("tok"), 3)
    return out


def build_codes(index: dict) -> None:
    gen = ROOT / "gen"
    if not gen.is_dir():
        return
    for gd in sorted(p for p in gen.iterdir() if p.is_dir()):
        offs = jl(gd / "offsets.jsonl")
        if not offs:
            continue
        name = gd.name
        manifest = {m.get("path"): m for m in jl(gd / "manifest.jsonl")}
        rep = jload(ROOT / "reports" / f"{name}_code.json")
        vc = isinstance(rep, dict) and "d1" in rep and "totals" in rep      # tools/verify_code.py schema
        statuses = {} if vc else (per_file_status(rep) if rep else {})
        fails = failures_verify_code(rep) if vc else (walk_failures(rep) if rep else [])
        if vc:
            for r in rep.get("files") or []:
                if r.get("parse_ok") is False or r.get("terminated") is False:
                    statuses[r["path"]] = "fail"
        files, by_path = [], {}
        srcdir = LIVE / "src" / name
        for o in offs:
            p = o.get("path")
            if not p:
                continue
            f = {"path": p, "pkg": p.split("/")[1] if p.startswith("recallstorm/") and p.count("/") > 1 else p.split("/")[0],
                 "start_tok": o.get("start_tok") or 0, "end_tok": o.get("end_tok") or o.get("start_tok") or 0,
                 "lines": o.get("lines"), "terminated": o.get("terminated", True),
                 "occurrence": o.get("occurrence", 1), "checks": {}}
            fp = [x for x in fails if x["path"] == p]
            for x in fp:
                f["checks"][x["check"]] = "FAIL"
            s = statuses.get(p)
            if s:
                f["status"] = norm_status(s)
            elif fp and max((x.get("severity") or 5) for x in fp) >= 5:
                f["status"] = "fail"
            elif fp:
                f["status"] = "warn"
            elif not f["terminated"]:
                f["status"] = "fail"; f["checks"]["unterminated"] = "FAIL"
            else:
                f["status"] = "pass" if rep else "unknown"
            wa = o.get("written_as")
            if wa and (gd / wa).is_file():
                dst = srcdir / (p + (".argon_reemitted" if wa.endswith(".argon_reemitted") else ""))
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(gd / wa, dst)
                f["src_url"] = f"live/src/{name}/{dst.relative_to(srcdir).as_posix()}"
            files.append(f)
            by_path[p] = f                       # last occurrence wins for edges
        # edges: deps.jsonl from the verifier, else the manifest's depends_on (unverified)
        dep_rows = []
        for cand in (ROOT / "reports" / f"{name}_deps.jsonl", ROOT / "reports" / name / "deps.jsonl",
                     gd / "deps.jsonl", ROOT / "reports" / "deps.jsonl"):
            dep_rows = jl(cand)
            if dep_rows:
                break
        if not dep_rows and isinstance(rep, dict) and isinstance(rep.get("deps"), list):
            dep_rows = rep["deps"]
        edges, agg = [], {}
        for r in dep_rows:
            s = r.get("from_path") or r.get("src") or r.get("from") or r.get("importer") or r.get("use_path")
            d = r.get("to_path") or r.get("dst") or r.get("to") or r.get("imported") or r.get("def_path")
            if not s or not d:
                continue
            st = r.get("status")
            if st in ("stdlib", "external"):
                continue                              # not a cross-file edge inside the generation
            if st is None and "ok" in r:
                st = "ok" if r["ok"] else "broken"
            st = "ok" if str(st).lower() in ("ok", "pass", "passed", "submodule") else (
                "broken" if st else "unknown")
            ut = r.get("use_tok") or r.get("use_pos") or (by_path.get(s) or {}).get("start_tok")
            dt = r.get("def_tok") or r.get("def_pos") or (by_path.get(d) or {}).get("start_tok")
            if isinstance(ut, (list, tuple)):
                ut = ut[0]
            if isinstance(dt, (list, tuple)):
                dt = dt[0]
            dist = r.get("distance") if r.get("distance") is not None else (
                (ut - dt) if ut is not None and dt is not None else None)
            sym = r.get("symbol")
            det = r.get("detail") or r.get("message")
            key = (s, d)
            e = agg.get(key)
            if e is None:
                e = agg[key] = {"src": s, "dst": d, "status": st, "use_tok": ut, "def_tok": dt, "distance": dist,
                                "symbols": [], "detail": None, "n": 0}
                edges.append(e)
            e["n"] += 1
            if sym and sym not in e["symbols"] and len(e["symbols"]) < 12:
                e["symbols"].append(sym)
            if st == "broken" or (st == "unknown" and e["status"] == "ok"):
                e["status"] = st
                e["detail"] = (f"{sym}: " if sym else "") + str(det or r.get("status"))
            if dist is not None and (e["distance"] is None or dist > e["distance"]):
                e["distance"] = dist; e["use_tok"] = ut; e["def_tok"] = dt
        for e in edges:
            if not e["detail"] and e["symbols"]:
                e["detail"] = ", ".join(e["symbols"])
        if not edges:
            for p, m in manifest.items():
                for d in m.get("depends_on") or []:
                    if p in by_path and d in by_path:
                        edges.append({"src": p, "dst": d, "status": "unverified",
                                      "use_tok": by_path[p]["start_tok"], "def_tok": by_path[d]["start_tok"],
                                      "distance": by_path[p]["start_tok"] - by_path[d]["start_tok"]})
        for x in fails:                             # token position + bucket for the gallery
            f = by_path.get(x["path"])
            if f and x.get("tok") is None:
                frac = (x["line"] / f["lines"]) if x.get("line") and f.get("lines") else 0
                x["tok"] = int(f["start_tok"] + (f["end_tok"] - f["start_tok"]) * min(1, frac))
            x["bucket"] = bucket_of(x.get("tok"))
        total = max([f["end_tok"] for f in files] + [1])
        summary = {"files": len(files), "pass": sum(f["status"] == "pass" for f in files),
                   "fail": sum(f["status"] == "fail" for f in files), "edges": len(edges),
                   "edges_broken": sum(e["status"] == "broken" for e in edges),
                   "report": f"reports/{name}_code.json" if rep else None,
                   "totals": rep.get("totals") if isinstance(rep, dict) else None,
                   "report_summary": {k: v for k, v in (rep or {}).items()
                                      if isinstance(v, (int, float, str)) or k in ("buckets", "summary", "by_bucket")}
                   if isinstance(rep, dict) else None}
        dump(f"code_{name}.json", {"name": name, "fixture": False, "total_tok": total, "files": files,
                                   "edges": edges, "failures": fails, "summary": summary})
        index["codes"].append(name)


# ------------------------------------------------------------------ verifier (Layer 2)
METRIC_KEYS = {"recall": ("recall", "pull_recall"), "precision": ("precision", "pull_precision"),
               "decoys_pulled": ("decoys_pulled", "decoys"), "hard_errors": ("hard_errors", "n_hard_errors",
                                                                             "hard_error_count")}


def find_key(node, names, depth=0):
    if depth > 4:
        return None
    if isinstance(node, dict):
        for k in names:
            if k in node and isinstance(node[k], (int, float)):
                return node[k]
        for v in node.values():
            r = find_key(v, names, depth + 1)
            if r is not None:
                return r
    return None


def build_verify(index: dict) -> None:
    rd = ROOT / "reports"
    if not rd.is_dir():
        return
    out = []
    for p in sorted(rd.glob("*_plan.json")):
        rep = jload(p)
        if not isinstance(rep, dict):
            continue
        name = p.name[: -len("_plan.json")]
        metrics = {k: find_key(rep, names) for k, names in METRIC_KEYS.items()}
        cov = rep.get("coverage") if isinstance(rep.get("coverage"), dict) else {}
        if cov.get("rate") is not None:
            metrics["coverage"] = cov["rate"]
        groups = None
        if isinstance(rep.get("by_check"), dict):                 # tools/verify_plan.py schema
            groups = {k: (v.get("hard", 0) if isinstance(v, dict) else v) for k, v in rep["by_check"].items()}
            soft = {k: v.get("soft", 0) for k, v in rep["by_check"].items() if isinstance(v, dict)}
        if isinstance(rep.get("errors"), list) and rep["errors"] and isinstance(rep["errors"][0], dict) \
                and "src" in rep["errors"][0]:
            hard = [e for e in rep["errors"] if e.get("severity") == "hard"]
            rest = [e for e in rep["errors"] if e.get("severity") != "hard"]
            errs = [{"group": f"{e.get('check')}:{e.get('severity')}", "src": e.get("src"),
                     "message": str(e.get("msg") or e.get("message") or "")[:400], "id": e.get("id"),
                     "plan_line": e.get("line"), "severity": 7 if e.get("severity") == "hard" else 3}
                    for e in (hard[:150] + rest[:50])]
        else:
            errs = [{"group": e["check"], "src": e["path"], "message": e["message"]} for e in walk_failures(rep)[:200]]
        by_src = rep.get("errors_by_src") or rep.get("by_src") or {}
        if isinstance(by_src, dict):
            by_src = {k: (len(v) if isinstance(v, list) else
                          (sum(v.get("counts", {}).values()) if isinstance(v, dict) and "counts" in v else v))
                      for k, v in by_src.items()}
        cls = rep.get("classification") if isinstance(rep.get("classification"), dict) else {}
        out.append({"name": name, "fixture": False, "report": f"reports/{p.name}", "metrics": metrics,
                    "groups": groups, "soft": soft if groups is not None else None, "errors": errs,
                    "errors_by_src": by_src,
                    "classification": {k: cls.get(k) for k in ("labeled", "tp", "fp", "fn", "confusion", "decoys")
                                       if k in cls},
                    "records": rep.get("records")})
    for p in sorted(rd.glob("accept_*.xml")):
        txt = p.read_text(errors="replace")[:4000]
        m = re.search(r'tests="(\d+)".*?failures="(\d+)"|failures="(\d+)".*?tests="(\d+)"', txt, re.S)
        errors = re.search(r'errors="(\d+)"', txt)
        if m:
            tests = int(m.group(1) or m.group(4)); failures = int(m.group(2) or m.group(3))
            out.append({"name": p.stem, "fixture": False, "report": f"reports/{p.name}", "kind": "acceptance",
                        "metrics": {"tests": tests, "failures": failures,
                                    "errors": int(errors.group(1)) if errors else 0}})
    if out:
        dump("verify.json", out)
        index["verify"] = True


def build_once() -> dict:
    global SIG
    SIG = hashlib.sha1()
    FILE_SIGS.clear()
    index = {"fixture": False, "built_at": time.strftime("%Y-%m-%d %H:%M:%S"), "drills": [], "runs": [],
             "codes": [], "verify": False}
    for fn in (build_drills, build_runs, build_codes, build_verify):
        try:
            fn(index)
        except Exception as e:
            print(f"  {fn.__name__} failed: {e!r}", file=sys.stderr)
    index["sig"] = SIG.hexdigest()[:16]          # the viewer auto-reloads only when this changes
    index["files"] = dict(FILE_SIGS)              # per-file content hash: unchanged files are not re-fetched
    dump("index.json", index)
    print(f"viewer data @ {index['built_at']}: drills={index['drills']} runs={index['runs']} "
          f"codes={index['codes']} verify={index['verify']}")
    return index


if __name__ == "__main__":
    if "--watch" in sys.argv:
        while True:
            build_once(); time.sleep(20)
    else:
        build_once()
