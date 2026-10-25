"""OURS. Baseline C CLI: python -m recallstorm run --scenario ID --data DIR --out DIR

Same pipeline as Baseline D, plus the RAG + gemini-4-argon classifier for items the rules mark HOLD_VERIFY.
Needs GEMINI_API_KEY in the environment unless every answer is already cached.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter
from datetime import datetime

PRICE_IN, PRICE_OUT = 2.0, 10.0          # $ per 1M tokens (thinking billed as output)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="recallstorm")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--scenario", required=True)
    r.add_argument("--data", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--max-calls", type=int, default=300)
    a = ap.parse_args(argv)

    from contract import load_datapack
    from . import rules
    from .classifier import ArgonClassifier
    from .plan import run

    pack = load_datapack(a.data)
    scen = json.loads((pathlib.Path(a.data) / f"scenario_{a.scenario}.json").read_text())
    state, at = scen.get("state", "CA"), datetime.fromisoformat(scen["deadline"])
    base = {s.sku_id: rules.evaluate_sku(s, pack.rules, state, at) for s in pack.skus}   # D's rules alone
    clf = ArgonClassifier(pack.rules, max_calls=a.max_calls)
    todo = [(s, sorted((x for x in rules.applicable_rules(s, pack.rules, state)
                        if at.replace(tzinfo=None) >= x.effective), key=lambda x: x.rule_id))
            for s in sorted(pack.skus, key=lambda s: s.sku_id) if base[s.sku_id].verdict.value == "HOLD_VERIFY"]
    clf.prefetch(todo)
    stats = run(a.scenario, a.data, a.out, classifier=clf, generator="baseline_c")

    plan = [json.loads(l) for l in (pathlib.Path(a.out) / "plan.jsonl").read_text().splitlines()]
    after = {x["sku_id"]: x["verdict"] for x in plan if x["type"] == "sku_verdict"}
    changed = Counter(f"{base[k].verdict.value}->{v}" for k, v in after.items() if v != base[k].verdict.value)
    st = clf.stats
    tin, tout = st["tok_prompt"], st["tok_output"] + st["tok_thoughts"]
    usage = {"model": "gemini-4-argon", "consulted": st["consulted"], "live_calls_this_run": st["live_calls"],
             "cache_hits": st["cache_hits"], "errors": st["errors"], "capped": st["capped"],
             "tokens": {"input": tin, "output_visible": st["tok_output"], "thinking": st["tok_thoughts"]},
             "est_cost_usd": round(tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT, 4),
             "verdict_changes_vs_d": dict(changed), "run": stats}
    (pathlib.Path(a.out) / "llm_usage.json").write_text(json.dumps(usage, indent=2) + "\n")
    print(json.dumps(usage, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
