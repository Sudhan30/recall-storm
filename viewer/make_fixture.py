"""OURS (P4). Writes FAKE fixture data into viewer/data/fixture/ so every view renders before real
artifacts exist. Everything here is invented; the viewer shows a FIXTURE badge whenever it is used.

Usage: python3 viewer/make_fixture.py        (deterministic, seed 7; reads data/ when present)

Formats written are the same normalized formats build_data.py writes into viewer/data/live/.
"""
from __future__ import annotations

import csv
import json
import pathlib
import random
import re
import zlib
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "viewer" / "data" / "fixture"
R = random.Random(7)
TZ = timezone(timedelta(hours=-8))


def jl(p: pathlib.Path) -> list[dict]:
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows


def dump(name: str, obj) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, separators=(",", ":")), encoding="utf-8")
    print("wrote", OUT / name, (OUT / name).stat().st_size, "bytes")


# ------------------------------------------------------------------ drill (map + 3D store)
ALIASES = ["FD&C Red No. 3", "FD&C Red #3", "Red No. 3", "Red Dye 3", "Red 3", "RED3", "erythrosine",
           "erythros1ne", "eritrosina", "E127", "E 127"]
ALIAS_RE = re.compile("|".join(re.escape(a) for a in sorted(ALIASES, key=len, reverse=True)), re.I)
UNCLEAR_RE = re.compile(r"artificial colou?rs?|color added", re.I)


def fake_stores() -> list[dict]:
    cities = [("Sacramento", 38.56, -121.49), ("Fresno", 36.74, -119.78), ("Los Angeles", 34.05, -118.24),
              ("San Diego", 32.72, -117.16), ("San Jose", 37.34, -121.89), ("Redding", 40.59, -122.39),
              ("Bakersfield", 35.37, -119.02), ("Riverside", 33.95, -117.40)]
    fm = ["SUPERCENTER", "NEIGHBORHOOD", "DISCOUNT", "SAMS"]
    return [{"store_id": f"CA{1000+i}", "format": fm[i % 4], "state": "CA", "city": c, "lat": la, "lon": lo,
             "district": "D01", "dc_id": "DC_NORTH" if la > 37 else ("DC_CENTRAL" if la > 35 else "DC_SOUTH"),
             "tz": "America/Los_Angeles"} for i, (c, la, lo) in enumerate(cities)]


def drill() -> dict:
    stores = jl(ROOT / "data" / "stores.jsonl") or fake_stores()
    skus = {s["sku_id"]: s for s in jl(ROOT / "data" / "skus.jsonl")}
    facings = jl(ROOT / "data" / "facings.jsonl")
    assoc = jl(ROOT / "data" / "associates.jsonl")
    labels = {}
    lp = ROOT / "data" / "labels.csv"
    if lp.exists():
        labels = {r["sku_id"]: r["truth"] for r in csv.DictReader(lp.open())}
    # keep the committed fixture small: 6 stores spread north to south, <= 360 facings each
    stores = sorted(stores, key=lambda s: -(s.get("lat") or 0))
    if len(stores) > 6:
        stores = [stores[round(i * (len(stores) - 1) / 5)] for i in range(6)]
    keep_ids = {s["store_id"] for s in stores}
    per: dict[str, list] = {}
    for f in facings:
        if f["store_id"] in keep_ids:
            per.setdefault(f["store_id"], []).append(f)
    facings = [f for v in per.values() for f in v[:360]]
    assoc = [a for a in assoc if a.get("store_id") in keep_ids]
    if not skus:  # nothing at all: invent a tiny catalog
        for i in range(30):
            ing = ["sugar, corn syrup, erythrosine", "sugar, artificial color", "sugar, Red 40, citric acid"][i % 3]
            skus[f"SKU{i:05d}"] = {"sku_id": f"SKU{i:05d}", "gtin": f"{i:014d}", "name": f"Fixture item {i}",
                                   "brand": "Fixture", "category": "candy", "ingredients": ing}
            labels[f"SKU{i:05d}"] = ["PULL", "HOLD_VERIFY", "KEEP"][i % 3]
    if not facings:
        for s in stores:
            for k, sid in enumerate(skus):
                facings.append({"store_id": s["store_id"], "sku_id": sid,
                                "loc": {"aisle": f"A{k // 30 + 1:02d}", "bay": k // 6 % 5 + 1,
                                        "shelf": k % 5 + 1, "pos": k % 6 + 1}, "units": 12})

    verdicts, evidence = [], []
    for sid, s in skus.items():
        truth = labels.get(sid)
        ing = s.get("ingredients", "")
        m = ALIAS_RE.search(ing)
        if truth is None:
            truth = "PULL" if m else ("HOLD_VERIFY" if UNCLEAR_RE.search(ing) else "KEEP")
        if truth == "PULL" and m:
            match = {"text": m.group(0), "start": m.start(), "end": m.end()}
        elif truth == "HOLD_VERIFY":
            u = UNCLEAR_RE.search(ing)
            match = {"text": u.group(0), "start": u.start(), "end": u.end()} if u else None
        else:
            match = None
        eid = f"EV-{sid}"
        verdicts.append({"type": "sku_verdict", "sku_id": sid, "gtin": s.get("gtin"), "verdict": truth,
                         "additive": "RED3" if truth == "PULL" else None, "match": match,
                         "rule_ids": ["CA_AB418_RED3"] if truth != "KEEP" else [], "jurisdictions": ["CA"],
                         "decided_by": "MODEL" if truth == "HOLD_VERIFY" else "RULE", "evidence_id": eid,
                         "src": "fixture/rules.py"})
        rationale = {"PULL": f"Ingredient text names Red No. 3 as '{match['text'] if match else '?'}'; "
                             "food sold in CA on or after 2027-01-01 00:00 local.",
                     "HOLD_VERIFY": "Label says only a generic color; cannot rule out Red No. 3. Hold and verify.",
                     "KEEP": "No Red No. 3 alias found (Red 40 / D&C Red 33 / similar are not Red No. 3)."}[truth]
        evidence.append({"type": "evidence", "evidence_id": eid, "sku_id": sid, "rule_id": "CA_AB418_RED3",
                         "clause_ref": "Cal. Health & Safety Code 109025(a)",
                         "source_span": "shall not ... sell ... a food product ... that contains ... (4) Red dye 3.",
                         "rationale": rationale, "src": "fixture/evidence.py"})
    vmap = {v["sku_id"]: v["verdict"] for v in verdicts}

    by_store_assoc: dict[str, list[str]] = {}
    for a in assoc:
        if a.get("store_id"):
            by_store_assoc.setdefault(a["store_id"], []).append(a["associate_id"])
    tasks, events = [], []
    t_start = datetime(2026, 12, 30, 22, 0, tzinfo=TZ)
    store_ids = [s["store_id"] for s in stores]
    for si, st in enumerate(store_ids):
        hit = [f for f in facings if f["store_id"] == st and vmap.get(f["sku_id"]) in ("PULL", "HOLD_VERIFY")]
        hit.sort(key=lambda f: (f["loc"]["aisle"], f["loc"]["bay"], f["loc"]["shelf"], f["loc"]["pos"]))
        people = by_store_assoc.get(st) or [f"{st}-A{i:02d}" for i in range(4)]
        people = people[: max(2, min(len(people), 6))]
        clock = {p: t_start + timedelta(minutes=R.randint(0, 40) + si * 7) for p in people}
        for k, f in enumerate(hit):
            p = people[k % len(people)]
            act = "PULL" if vmap[f["sku_id"]] == "PULL" else "HOLD_VERIFY"
            tid = f"T-{st}-{k:04d}"
            subs = None
            t0 = clock[p]
            t_move = t0 + timedelta(minutes=R.uniform(1.5, 4))
            t_pull = t_move + timedelta(minutes=R.uniform(2, 5))
            t_done = t_pull + timedelta(minutes=R.uniform(1, 3))
            tasks.append({"type": "shelf_task", "task_id": tid, "store_id": st, "sku_id": f["sku_id"],
                          "action": act, "loc": f["loc"], "qty_units": f.get("units", 0), "associate_id": p,
                          "window": [t0.isoformat(), t_done.isoformat()], "seq": k, "evidence_id": f"EV-{f['sku_id']}",
                          "sub_sku_id": subs, "alloc_id": None, "src": "fixture/plan.py"})
            ev = lambda t, kind: {"t": t.isoformat(), "store_id": st, "associate_id": p, "kind": kind,
                                  "loc": f["loc"], "task_id": tid}
            events += [ev(t_move, "MOVE"), ev(t_pull, "PULL")]
            if act == "PULL" and R.random() < 0.6:
                t_place = t_pull + timedelta(minutes=R.uniform(1, 2))
                events.append(ev(t_place, "PLACE")); t_done = t_place + timedelta(minutes=1)
            events.append(ev(t_done, "DONE"))
            clock[p] = t_done
    events.sort(key=lambda e: e["t"])
    used = {f["sku_id"] for f in facings}
    verdicts = [v for v in verdicts if v["sku_id"] in used]
    evidence = [e for e in evidence if e["sku_id"] in used]
    return {"name": "core", "fixture": True,
            "source": {"stores": "data/stores.jsonl" if (ROOT / "data/stores.jsonl").exists() else "invented",
                       "events": "FIXTURE (invented replay)", "plan": "FIXTURE (from labels.csv truth)"},
            "stores": stores,
            "rules": jl(ROOT / "data" / "rules.jsonl"),
            "facings": facings,
            "skus": {k: {"name": v.get("name"), "brand": v.get("brand"), "category": v.get("category"),
                         "ingredients": v.get("ingredients", "")} for k, v in skus.items() if k in used},
            "plan": {"sku_verdict": verdicts, "evidence": evidence, "shelf_task": tasks, "store_playbook": []},
            "events": events}


# ------------------------------------------------------------------ run (hops & seams)
def run_fixture(name: str, total: int, hop_size: int, tps: float, prompt: int) -> dict:
    points, hops, seams = [[0, 0, 0]], [], []
    t, vis, think, byte = 0.0, 0, 0, 0
    h = 0
    while vis < total:
        hv = min(hop_size - R.randint(0, 900), total - vis)
        hthink = int(hv * 0.13)
        steps = 40
        for s in range(1, steps + 1):
            t += hv / steps / (tps * R.uniform(0.85, 1.15))
            points.append([round(t, 1), vis + hv * s // steps, think + hthink * s // steps])
        vis += hv; think += hthink; byte += int(hv * 3.4)
        last = vis >= total
        hops.append({"hop": h, "t": round(t, 1), "visible_hop": hv, "thinking_hop": hthink, "prompt_hop": prompt,
                     "visible_total": vis, "seam_byte": byte, "finish": "STOP" if last else "CONTINUATION",
                     "has_token": not last})
        if not last:
            seams.append({"n": h + 1, "hop": h, "t": round(t, 1), "tok": vis, "seam_byte": byte, "status": "PASS",
                          "fails": [], "notes": [],
                          "before": "    return [a for a in allocs if a.qty_cases > 0]\n\n\ndef rebalance(allocs: list[Allocation],",
                          "after": " stock: list[DcStock]) -> list[Allocation]:\n    \"\"\"Move cases between stores ...\"\"\""})
        t += R.uniform(2, 6)
        h += 1
    cost = (vis + think) * 10 / 1e6 + prompt * len(hops) * 2 / 1e6
    return {"name": name, "fixture": True, "kind": "run", "points": points, "hops": hops, "seams": seams,
            "summary": {"visible": vis, "thinking": think, "prompt": prompt * len(hops), "hops": len(hops),
                        "minutes": round(t / 60, 1), "cost_usd": round(cost, 2), "live": False,
                        "seams_pass": len(seams), "seams_fail": 0}}


# ------------------------------------------------------------------ code wall + failures
PKGS = [("core", 6), ("ingest", 22), ("aliases", 10), ("rules", 26), ("adjudicate", 12), ("gs1", 16),
        ("store", 14), ("labor", 14), ("allocate", 14), ("plan", 18), ("sim", 12), ("recall_lots", 10),
        ("route", 14), ("cli", 6), ("integration", 28), ("docs", 14)]
CHECKS = ["D1", "D2", "D3", "D4", "D6"]
MSGS = {"D1": "manifest promises {sym}() with 3 args; file defines it with 2",
        "D2": "import {sym} from recallstorm.{dep} does not resolve",
        "D3": "string literal 'PULLED' is not in contract enums (Action / Verdict)",
        "D4": "pytest: AssertionError in test_{sym} (expected 12 cases, got 11)",
        "D6": "8-line window duplicated from {dep_path}"}


def fake_source(path: str, deps: list[str], n_funcs: int, broken_line: int | None) -> str:
    mod = path.replace("/", ".").removesuffix(".py")
    out = [f'"""FIXTURE source for {path}. Invented text; not Argon output."""',
           "from __future__ import annotations", "from contract import Sku, Store, Rule, Verdict, Action"]
    for d in deps:
        out.append(f"from {d.replace('/', '.').removesuffix('.py')} import helper_{zlib.crc32(d.encode()) % 97}")
    out.append("")
    for i in range(n_funcs):
        out += ["", f"def fn_{i}(items: list[Sku], at: str) -> list[str]:",
                f'    """Docstring for {mod}.fn_{i}."""',
                "    if not items:", "        raise ValueError('empty input')",
                "    out = []", "    for it in items:",
                "        if it.is_food:", f"            out.append(it.sku_id + ':{i}')", "    return sorted(out)"]
    if broken_line:
        out.insert(min(broken_line, len(out)), "    return 'PULLED'  # fixture: deliberately wrong code value")
    return "\n".join(out) + "\n"


def code_fixture() -> dict:
    files, tok = [], 0
    for pkg, n in PKGS:
        for i in range(n):
            if pkg in ("integration",):
                path = f"tests/integration/test_{pkg}_{i:02d}.py"
            elif pkg == "docs":
                path = f"docs/{pkg}_{i:02d}.md"
            elif i % 4 == 3:
                path = f"tests/unit/test_{pkg}_{i:02d}.py"
            else:
                path = f"recallstorm/{pkg}/mod_{i:02d}.py"
            size = R.randint(1500, 5200)
            files.append({"path": path, "pkg": pkg, "start_tok": tok, "end_tok": tok + size})
            tok += size
    scale = 760_000 / tok
    for f in files:
        f["start_tok"] = int(f["start_tok"] * scale); f["end_tok"] = int(f["end_tok"] * scale)
    edges, failures, sources = [], [], {}
    for idx, f in enumerate(files):
        pos = f["start_tok"] / 760_000
        deps = []
        if idx > 0 and not f["path"].startswith("docs/"):
            k = R.randint(1, 3 if pos < 0.8 else 5)
            for _ in range(k):
                j = R.randint(0, idx - 1) if R.random() < 0.6 else R.randint(max(0, idx - 12), idx - 1)
                if files[j]["path"].endswith(".py") and files[j]["path"] not in deps:
                    deps.append(files[j]["path"])
        fail_p = 0.03 + 0.30 * pos ** 2          # invented: more failures late in the stream
        bad = R.random() < fail_p
        n_funcs = R.randint(3, 8)
        broken = R.randint(8, 8 + n_funcs * 8) if bad else None
        src = fake_source(f["path"], deps, n_funcs, broken)
        sources[f["path"]] = src
        f["lines"] = src.count("\n")
        f["status"] = "fail" if bad else ("warn" if R.random() < 0.08 else "pass")
        f["checks"] = {}
        if bad:
            ck = R.choice(CHECKS)
            f["checks"][ck] = "FAIL"
            dep_path = deps[0] if deps else files[0]["path"]
            failures.append({"check": ck, "path": f["path"], "line": broken + 1,
                             "message": MSGS[ck].format(sym=f"fn_{R.randint(0, n_funcs - 1)}",
                                                         dep=dep_path.split("/")[1] if "/" in dep_path else "core",
                                                         dep_path=dep_path),
                             "tok": f["start_tok"] + int((f["end_tok"] - f["start_tok"]) * (broken / max(1, f["lines"]))),
                             "severity": 2 if ck in ("D2", "D4") else 1})
        for d in deps:
            dj = next(x for x in files if x["path"] == d)
            st = "broken" if (bad and R.random() < 0.5) else "ok"
            edges.append({"src": f["path"], "dst": d, "status": st, "use_tok": f["start_tok"] + 40,
                          "def_tok": dj["start_tok"], "distance": f["start_tok"] - dj["start_tok"]})
    summary = {"files": len(files), "pass": sum(f["status"] == "pass" for f in files),
               "fail": sum(f["status"] == "fail" for f in files), "edges": len(edges),
               "edges_broken": sum(e["status"] == "broken" for e in edges)}
    return {"name": "expansion", "fixture": True, "total_tok": 760_000, "files": files, "edges": edges,
            "failures": failures, "summary": summary, "sources": sources}


def verifier_fixture() -> list[dict]:
    return [{"name": "core", "fixture": True,
             "metrics": {"recall": 0.97, "precision": 0.95, "decoys_pulled": 0, "hard_errors": 0},
             "groups": {"reference": 0, "conservation": 0, "capacity": 0, "labor": 0, "deadline": 0},
             "errors": [], "errors_by_src": {}},
            {"name": "expansion", "fixture": True,
             "metrics": {"recall": 0.88, "precision": 0.91, "decoys_pulled": 1, "hard_errors": 7},
             "groups": {"reference": 3, "conservation": 1, "capacity": 0, "labor": 2, "deadline": 1},
             "errors": [{"group": "reference", "src": "recallstorm/route/mod_05.py",
                         "message": "route_manifest MAN-0007 references alloc_id AL-0091 that no allocation record has"},
                        {"group": "deadline", "src": "recallstorm/plan/mod_09.py",
                         "message": "shelf_task T-CA1004-0012 window ends 2027-01-01T00:30 local, after the deadline"},
                        {"group": "labor", "src": "recallstorm/labor/mod_02.py",
                         "message": "associate CA1003-A04 has overlapping windows 23:10-23:40 and 23:30-23:55"}],
             "errors_by_src": {"recallstorm/route/mod_05.py": 3, "recallstorm/plan/mod_09.py": 1,
                               "recallstorm/labor/mod_02.py": 2, "recallstorm/allocate/mod_06.py": 1}}]


def main() -> None:
    d = drill()
    dump("drill_core.json", d)
    dump("run_expansion.json", run_fixture("expansion", 760_000, 64_000, 95.0, 30_000))
    dump("run_core.json", run_fixture("core", 52_000, 64_000, 110.0, 18_000))
    dump("code_expansion.json", code_fixture())
    dump("verify.json", verifier_fixture())
    dump("index.json", {"fixture": True, "built_at": "fixture", "drills": ["core"],
                        "runs": ["expansion", "core"], "codes": ["expansion"], "verify": True})


if __name__ == "__main__":
    main()
