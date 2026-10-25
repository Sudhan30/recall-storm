"""OURS. Thin adapter: runs gen/expansion (v1, Argon-generated, unedited) on the fda_lots scenario.

v1's CLI (`python -m recallstorm run`) has no lot scenario path: cmd_run always calls plan.assemble_plan (the
Red No. 3 pipeline). The lot code lives in recallstorm.scenario_gs1 and is reachable only as a library:
    scenario.recall_from_openfda(raw openFDA report) -> Gs1Scenario (ONE recall: gtins, lot_codes, as_of, deadline)
    scenario.recall_plan(Gs1Scenario, DataPack)      -> evidence + shelf_task records
v1 reads a contract DataPack (load_datapack: data/*.jsonl), where Facing has no lot field.

What this adapter does (nothing under gen/ is edited):
  1. Writes an adapter data dir (out/fda_lots_v1_data/): skus.jsonl <- skus_fda.jsonl, facings.jsonl <- one
     contract Facing per simulated shelf lot (same store/sku/loc/units, lot dropped), stores/associates/trucks
     copied, no rules/dc_stock/substitutes/notes, scenario_fda_lots.json copied.
  2. Mode `gs1` (v1 as written): per scenario recall, v1's recall_from_openfda(raw report) -- v1's own parser
     picks the lots -- then dataclasses.replace(gtins=(our simulated item-master GTIN,), as_of, deadline from
     our scenario) because the notice's real UPCs are not our simulated SKUs' GTINs; then v1's recall_plan.
     Records concatenated, plus one adapter `run` record. Per-recall exceptions -> tracebacks file.
  3. Mode `gs1_lotinv` (v1 lot matcher with the shelf lots the v1 recall_plan never passes): same scenarios, but
     calls v1's lot_pull_tasks once per shelf lot with lot_inventory={(store, sku): [that lot]} and v1's own
     window/associate choice from recall_plan. Because v1 restarts seq per call, the adapter suffixes task_id
     with the lot's loc to keep ids unique (adapter-side, documented).
  4. Mode `cli`: runs v1's real CLI on the adapter data dir: python -m recallstorm run --scenario fda_lots ...

Usage: .venv/bin/python scenarios/fda_lots/adapter.py --mode gs1|gs1_lotinv|cli [--out out/<name>/]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import pathlib
import shutil
import subprocess
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = pathlib.Path(os.environ.get("RECALLSTORM_GEN", ROOT / "gen" / "expansion"))  # repair loop points this at a patched copy
SRC = "scenarios/fda_lots/adapter.py"


def jl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]


def wj(p, rows):
    pathlib.Path(p).write_text("".join(json.dumps(r) + "\n" for r in rows))


def build_data_dir(dst: pathlib.Path) -> pathlib.Path:
    D = ROOT / "data"
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("stores.jsonl", "associates.jsonl", "trucks.jsonl", "scenario_fda_lots.json"):
        shutil.copy(D / f, dst / f)
    shutil.copy(D / "skus_fda.jsonl", dst / "skus.jsonl")
    wj(dst / "facings.jsonl", [{"store_id": x["store_id"], "sku_id": x["sku_id"], "loc": x["loc"], "units": x["units"]}
                               for x in jl(D / "lots.jsonl")])
    for f in ("rules.jsonl", "dc_stock.jsonl", "notes.jsonl"):
        (dst / f).write_text("")
    (dst / "substitutes.json").write_text("{}")
    return dst


RAW_KEYS = ("recall_number", "event_id", "status", "recalling_firm", "product_description", "reason_for_recall",
            "classification", "report_date", "distribution_pattern", "code_info")


def run_gs1(data_dir: pathlib.Path, out: pathlib.Path, lotinv: bool) -> int:
    sys.path[:0] = [str(GEN), str(ROOT)]
    from contract import load_datapack, Facing                       # ours (contract_io)
    from recallstorm.scenario_gs1.scenario import recall_from_openfda, recall_plan   # v1
    from recallstorm.scenario_gs1.lot_pull import lot_pull_tasks, lot_evidence       # v1
    scen = json.loads((data_dir / "scenario_fda_lots.json").read_text())
    pack = load_datapack(str(data_dir))
    lots = jl(ROOT / "data" / "lots.jsonl")
    recalls = {r["recall_number"]: r for r in jl(ROOT / "data" / "recalls_fda.jsonl")}
    recs = [{"type": "run", "run_id": f"expansion_v1_{'lotinv' if lotinv else 'gs1'}", "scenario_id": "fda_lots",
             "generator": "gen/expansion (v1) scenario_gs1 via adapter", "as_of": scen["as_of"],
             "rule_ids": [f"OPENFDA_{n}" for n in scen["recall_numbers"]], "src": SRC}]
    crashes, per_recall = [], []
    for n in scen["recall_numbers"]:
        r = recalls[n]
        raw = {k: r[k] for k in RAW_KEYS}
        try:
            g = recall_from_openfda(raw)
            g = dataclasses.replace(g, gtins=(r["sim_gtin"],), as_of=scen["as_of"], deadline=scen["deadline"])
            if not lotinv:
                out_recs = recall_plan(g, pack)
            else:
                matched_ids = {r["sim_sku_id"]}
                win = [g.as_of, "2026-12-31T06:00:00-08:00"]          # as recall_plan does
                out_recs = [lot_evidence(r["sim_sku_id"], l, g.recall_id) for l in g.lot_codes]
                for x in lots:
                    if x["sku_id"] != r["sim_sku_id"]:
                        continue
                    f = next(f for f in pack.facings if f.store_id == x["store_id"] and f.sku_id == x["sku_id"]
                             and dataclasses.asdict(f.loc) == x["loc"])
                    ts = lot_pull_tasks(x["store_id"], [f], matched_ids, list(g.lot_codes), f"{x['store_id']}-A00", win,
                                        lot_inventory={(x["store_id"], x["sku_id"]): [x["lot"]]}, recall_id=g.recall_id)
                    for t in ts:
                        L = x["loc"]
                        t["task_id"] += f"-{L['aisle']}{L['bay']}{L['shelf']}{L['pos']}"   # adapter: unique ids
                    out_recs += ts
            recs += out_recs
            per_recall.append({"recall_number": n, "v1_lot_codes": list(g.lot_codes), "v1_state": g.state,
                               "records": len(out_recs),
                               "shelf_tasks": sum(1 for x in out_recs if x.get("type") == "shelf_task")})
        except Exception as e:  # noqa: BLE001 -- capture every v1 crash honestly
            crashes.append({"recall_number": n, "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
    out.mkdir(parents=True, exist_ok=True)
    wj(out / "plan.jsonl", recs)
    (out / "adapter_log.json").write_text(json.dumps({"per_recall": per_recall, "crashes": crashes}, indent=2) + "\n")
    print(f"wrote {out/'plan.jsonl'}: {len(recs)} records, {sum(1 for x in recs if x.get('type')=='shelf_task')} "
          f"shelf_tasks; {len(crashes)} recalls crashed")
    return 0


def run_cli(data_dir: pathlib.Path, out: pathlib.Path) -> int:
    env = {**os.environ, "PYTHONPATH": f"{GEN}:{ROOT}"}
    out.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "recallstorm", "run", "--scenario", "fda_lots", "--data", str(data_dir), "--out", str(out)]
    p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    (out / "cli_log.txt").write_text(f"$ {' '.join(cmd)}\nexit {p.returncode}\n--- stdout\n{p.stdout}\n--- stderr\n{p.stderr}")
    print(f"cli exit {p.returncode}; log {out/'cli_log.txt'}")
    return p.returncode


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["gs1", "gs1_lotinv", "cli"], default="gs1")
    ap.add_argument("--out"); ap.add_argument("--data-dir", default=str(ROOT / "out" / "fda_lots_v1_data"))
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out or ROOT / "out" / {"gs1": "expansion_fda_lots", "gs1_lotinv": "expansion_fda_lots_lotinv",
                                                 "cli": "expansion_fda_lots_cli"}[a.mode])
    data_dir = build_data_dir(pathlib.Path(a.data_dir))
    return run_cli(data_dir, out) if a.mode == "cli" else run_gs1(data_dir, out, a.mode == "gs1_lotinv")


if __name__ == "__main__":
    sys.exit(main())
