"""OURS. Baseline D-lots: code only, no LLM, no gen/ code. Hand-written lot matcher + pull plan for fda_lots.

Reads only what a store-ops planner would have: the recall notices' raw text (code_info, distribution_pattern
from data/recalls_fda.jsonl -- NOT the parsed lots/date_windows/parse_confidence columns there, and never
labels_fda.csv), the item-master cross-reference (sim_sku_id), shelf lots (data/lots.jsonl), stores and
associates. Written separately from data/build_fda_lots.py's parser (same author, so not independent).

Rules: PULL a shelf lot when its normalized lot code is listed or inside a listed "X through Y" range, or (when
the notice lists no lots) its best-by date falls in a listed date / window; PULL every lot for "all lots";
HOLD_VERIFY every lot of a SKU whose notice is a numbered multi-product list, uses DD/MM dates, describes a lot
format / purchase or production dates, or yields nothing parseable. Skip recalls not distributed to the state.
Labor: each store's own associates, round-robin, 6-minute sequential slots from shift start.

Usage: python baselines/d_lots/plan_lots.py --scenario fda_lots --data data/ --out out/baseline_d_lots/
"""
from __future__ import annotations

import argparse
import calendar
import json
import pathlib
import re
from collections import defaultdict
from datetime import date, datetime, timedelta

SRC = "baselines/d_lots/plan_lots.py"
MON = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}


def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]


def nl(s: str) -> str:
    s = re.sub(r"^\s*(lot|batch)\s*[#:.-]?\s*", "", s, flags=re.I)
    return re.sub(r"[^0-9A-Za-z]", "", s).upper()


def y4(y):
    y = int(y); return y + 2000 if y < 100 else y


def dates_in(t):
    """[(pos, end, lo, hi)] for the common US label date formats; month-only -> whole month."""
    out, used = [], set()
    pats = [(r"(20\d\d)-(\d\d)-(\d\d)", lambda g: (int(g[0]), int(g[1]), int(g[2]))),
            (r"(\d{1,2})/(\d{1,2})/(\d{2,4})", lambda g: (y4(g[2]), int(g[0]), int(g[1]))),
            (r"(\d{1,2})\s*([A-Za-z]{3})[a-z]*\.?\s*,?\s*(20\d\d|\d\d)\b", lambda g: (y4(g[2]), MON.get(g[1].lower()), int(g[0]))),
            (r"\b([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(20\d\d)", lambda g: (int(g[2]), MON.get(g[0].lower()), int(g[1]))),
            (r"(20\d\d)\s+([A-Za-z]{3})[a-z]*\s+(\d{1,2})", lambda g: (int(g[0]), MON.get(g[1].lower()), int(g[2]))),
            (r"\b(\d{1,2})[/-](20\d\d)\b", lambda g: (int(g[1]), int(g[0]), None)),
            (r"\b([A-Za-z]{3})[a-z]*\s+(20\d\d)\b", lambda g: (int(g[1]), MON.get(g[0].lower()), None))]
    for pat, f in pats:
        for m in re.finditer(pat, t, re.I):
            if used & set(range(m.start(), m.end())):
                continue
            try:
                y, mo, d = f(m.groups())
                if not mo:
                    continue
                if d is None:
                    lo, hi = date(y, mo, 1), date(y, mo, calendar.monthrange(y, mo)[1])
                else:
                    lo = hi = date(y, mo, d)
            except (ValueError, TypeError):
                continue
            used |= set(range(m.start(), m.end())); out.append((m.start(), m.end(), lo, hi))
    return sorted(out)


def terms(ci: str):
    t = re.sub(r"[\r\n\t]", " ", ci or "")
    if (re.search(r"(?:^|\s)\d\s*[.)]\s.*\s\d\s*[.)]\s", t) or re.search(r"\b(1[3-9]|2\d|3[01])/\d{1,2}/\d{2,4}", t)
            or re.search(r"format|purchased|production|julian|no lot|not have any code|\bnone\b|unknown", t, re.I)):
        return {"mode": "hold"}
    if re.search(r"\ball (lots?|lot codes|codes)\b", t, re.I) and not re.search(r"through|before|up to", t, re.I):
        return {"mode": "all"}
    t2 = re.sub(r"(upc|product|item)\s*(number|no\.?|#)?\s*[:#]?\s*[\dA-Z][\dA-Z\s-]{4,}?(?=[,;]|\s{2}|\s[A-Za-z]|$)", " ", t, flags=re.I)
    ds = dates_in(t2)
    lots, ranges = set(), []
    mask = list(t2)
    for s, e, _, _ in ds:
        mask[s:e] = " " * (e - s)
    t3 = "".join(mask)
    for m in re.finditer(r"\b(?:lot|batch)[a-z]*\s*(?:#|no\.?|numbers?|codes?)?\s*[:#]?\s*(.*?)(?=\b(?:best|use|exp|bb|upc|sell|lot|batch|man|date)\b|$)",
                         t3, re.I):
        seg = m.group(1)
        for a, b in re.findall(r"([\w-]+)\s+(?:through|thru|to)\s+([\w-]+)", seg, re.I):
            ranges.append((nl(a), nl(b)))
        seg = re.sub(r"[\w-]+\s+(?:through|thru|to)\s+[\w-]+", ",", seg, flags=re.I)
        for tok in re.split(r"[,;]|\band\b|\s{2,}| - ", seg):
            tok = tok.strip(" .:#()")
            sub = tok.split() if len(tok.split()) > 1 and all(x.isdigit() for x in tok.split()) else [tok]
            for x in sub:
                if re.search(r"\d", x) and len(nl(x)) >= 3:
                    lots.add(nl(x))
    if lots or ranges:
        return {"mode": "lots", "lots": lots, "ranges": ranges}
    wins = []
    i = 0
    while i < len(ds):
        s, e, lo, hi = ds[i]
        if i + 1 < len(ds) and re.fullmatch(r"\s*(-|to|through|thru|up to and including)\s*", t2[e:ds[i + 1][0]], re.I):
            wins.append((lo, ds[i + 1][3])); i += 2; continue
        pre = t2[max(0, s - 60):s].lower()
        if re.search(r"(up to and including|on or before|up to|prior to|through)\s*:?\s*$", pre) or \
                (re.search(r"(?<!best )before\s*:?\s*$", pre)):
            strict = bool(re.search(r"(?<!or )(?<!best )before\s*:?\s*$|prior to\s*:?\s*$", pre))
            wins.append((date.min, hi - timedelta(days=1) if strict else hi))
        else:
            wins.append((lo, hi))
        i += 1
    if wins:
        return {"mode": "dates", "wins": wins}
    return {"mode": "hold"}


def decide(tm, lot, best_by):
    if tm["mode"] == "hold":
        return "HOLD_VERIFY"
    if tm["mode"] == "all":
        return "PULL"
    if tm["mode"] == "lots":
        n = nl(lot)
        if n in tm["lots"] or any(len(n) == len(a) == len(b) and a <= n <= b for a, b in tm["ranges"]):
            return "PULL"
        return None
    bb = date.fromisoformat(best_by)
    return "PULL" if any(lo <= bb <= hi for lo, hi in tm["wins"]) else None


def ships_to(pattern, state):
    names = {"CA": "california"}
    return bool(re.search(rf"\b{state}\b|{names.get(state, state)}|nationwide|nation wide|\bUSA?\b|U\.S\.|united states",
                          pattern or "", re.I))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="fda_lots"); ap.add_argument("--data", default="data")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    D = pathlib.Path(a.data)
    scen = json.loads((D / f"scenario_{a.scenario}.json").read_text())
    want = set(scen["recall_numbers"])
    recalls = [r for r in jl(D / "recalls_fda.jsonl") if r["recall_number"] in want]
    stores = {s["store_id"]: s for s in jl(D / "stores.jsonl")}
    assoc = defaultdict(list)
    for x in jl(D / "associates.jsonl"):
        if not x["is_floater"]:
            assoc[x["store_id"]].append(x)
    deadline = datetime.fromisoformat(scen["deadline"])
    by_sku = {}
    recs = [{"type": "run", "run_id": "baseline_d_lots", "scenario_id": scen["scenario_id"], "generator": "baseline_d_lots",
             "as_of": scen["as_of"], "rule_ids": [f"OPENFDA_{r['recall_number']}" for r in recalls], "src": SRC}]
    for r in recalls:
        if ships_to(r.get("distribution_pattern"), scen["state"]):
            by_sku[r["sim_sku_id"]] = (r, terms(r.get("code_info", "")))
    tasks = defaultdict(list)
    for x in jl(D / "lots.jsonl"):
        if x["sku_id"] not in by_sku or x["store_id"] not in stores:
            continue
        r, tm = by_sku[x["sku_id"]]
        act = decide(tm, x["lot"], x["best_by"])
        if act:
            tasks[x["store_id"]].append((act, x, r))
    for r, tm in by_sku.values():
        recs.append({"type": "evidence", "evidence_id": f"EV-{r['recall_number']}", "sku_id": r["sim_sku_id"],
                     "rule_id": f"OPENFDA_{r['recall_number']}", "clause_ref": f"openFDA {r['recall_number']} code_info",
                     "source_span": [0, len(r.get("code_info") or "")], "rationale": f"mode={tm['mode']}", "src": SRC})
    for sid in sorted(tasks):
        crew = sorted(assoc[sid], key=lambda x: x["associate_id"])
        nxt = {c["associate_id"]: datetime.fromisoformat(c["shift_start"]) for c in crew}
        ids, counts = [], defaultdict(int)
        for i, (act, x, r) in enumerate(sorted(tasks[sid], key=lambda t: (t[1]["loc"]["aisle"], t[1]["loc"]["bay"],
                                                                          t[1]["loc"]["shelf"], t[1]["loc"]["pos"]))):
            c = crew[i % len(crew)]
            s0 = nxt[c["associate_id"]]; s1 = s0 + timedelta(minutes=6)
            assert s1 <= datetime.fromisoformat(c["shift_end"]) and s1 < deadline
            nxt[c["associate_id"]] = s1
            tid = f"{sid}-LOT-{i:04d}"
            ids.append(c["associate_id"]); counts[act] += 1
            recs.append({"type": "shelf_task", "task_id": tid, "store_id": sid, "sku_id": x["sku_id"], "action": act,
                         "loc": x["loc"], "qty_units": x["units"], "associate_id": c["associate_id"],
                         "window": [s0.isoformat(), s1.isoformat()], "seq": i + 1,
                         "evidence_id": f"EV-{r['recall_number']}", "sub_sku_id": None, "alloc_id": None,
                         "lot": x["lot"], "src": SRC})
        recs.append({"type": "store_playbook", "store_id": sid, "format": stores[sid]["format"],
                     "deadline": scen["deadline"], "windows": [], "counts": dict(counts),
                     "associate_ids": sorted(set(ids)), "exception_ids": [], "manifest_ids": [], "src": SRC})
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "plan.jsonl").write_text("".join(json.dumps(x) + "\n" for x in recs))
    print(f"wrote {out/'plan.jsonl'}: {sum(1 for x in recs if x['type']=='shelf_task')} shelf_tasks")


if __name__ == "__main__":
    main()
