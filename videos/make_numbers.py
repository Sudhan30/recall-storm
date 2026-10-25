"""Build videos/numbers.json: every number the videos speak or show, read from its source file.

Run from repo root with any Python 3:  python3 videos/make_numbers.py
Each entry: {"value": ..., "source": "<file>", "field": "<how it was read>"}.
Keys whose source does not exist yet (expansion_v2) are written as null with "pending": true, and the
build renders a "[v2 numbers pending]" card instead of speaking them.
"""
import json, pathlib, re, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = {}


def put(key, value, source, field, **extra):
    N[key] = {"value": value, "source": source, "field": field, **extra}


def jload(p):
    return json.loads((ROOT / p).read_text())


def jl(p):
    f = ROOT / p
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


# --- working core: verify_plan reports
for name in ("core_patched", "core"):
    p = f"reports/{name}_plan.json"
    r = jload(p)
    c = r["classification"]
    put(f"{name}.hard_errors", r["hard_errors"], p, "hard_errors")
    put(f"{name}.precision", round(c["precision"], 3), p, "classification.precision (rounded to 3 dp)", raw=c["precision"])
    put(f"{name}.recall", round(c["recall"], 3), p, "classification.recall (rounded to 3 dp)", raw=c["recall"])
    put(f"{name}.fn", c["fn"], p, "classification.fn (missed PULLs)")
    put(f"{name}.decoys", c["decoys"], p, "classification.decoys")
    put(f"{name}.decoys_pulled", c["decoys_pulled"], p, "classification.decoys_pulled")
    put(f"{name}.labeled", c["labeled"], p, "classification.labeled (SKUs)")
    put(f"{name}.pull_facings", r["coverage"]["pull_facings"], p, "coverage.pull_facings")
    put(f"{name}.pull_facings_tasked", r["coverage"]["pull_facings_tasked"], p, "coverage.pull_facings_tasked")
    put(f"{name}.stores", r["records"]["store_playbook"], p, "records.store_playbook")
    put(f"{name}.shelf_tasks", r["records"]["shelf_task"], p, "records.shelf_task")
    put(f"{name}.events", r["events"]["events"], p, "events.events")
    put(f"{name}.deadline", r["deadline_local"], p, "deadline_local")
    put(f"{name}.coverage_hard", r["by_check"].get("coverage", {}).get("hard", 0), p, "by_check.coverage.hard")

log_md = (ROOT / "patches/LOG.md").read_text()
put("patches.core_count", len(re.findall(r"^## core/", log_md, re.M)), "patches/LOG.md", "count of '## core/' patch headings")
m = re.search(r"(\d+) passed, (\d+) skipped, before and after", log_md)
put("patches.argon_unit_passed", int(m.group(1)), "patches/LOG.md", "Argon's own unit tests passed (before and after)")

# --- managed-agent repair loop
for rec in jl("patches/agent/LOG.jsonl"):
    k = f"agent.{rec['name']}"
    put(f"{k}.result", rec["result"], "patches/agent/LOG.jsonl", f"{rec['name']}.result")
    put(f"{k}.secs", round(rec["secs"]), "patches/agent/LOG.jsonl", f"{rec['name']}.secs (rounded)", raw=rec["secs"])
    for side in ("before", "after"):
        if rec.get(side) and "failed" in rec[side]:
            put(f"{k}.{side}_failed", rec[side]["failed"], "patches/agent/LOG.jsonl", f"{rec['name']}.{side}.failed")
            put(f"{k}.{side}_passed", rec[side]["passed"], "patches/agent/LOG.jsonl", f"{rec['name']}.{side}.passed")
    h = rec.get("holdout")
    if h:
        put(f"{k}.held_out", h["held_out"], "patches/agent/LOG.jsonl", f"{rec['name']}.holdout.held_out")
        put(f"{k}.held_out_fixed", h["held_out_fixed"], "patches/agent/LOG.jsonl", f"{rec['name']}.holdout.held_out_fixed")
        put(f"{k}.new_failures", len(h["new_failures"]), "patches/agent/LOG.jsonl", f"len({rec['name']}.holdout.new_failures)")


# --- experiment: hops (v1 real, v2 pending until its run finishes)
def hops(run, prefix):
    rows = jl(f"runs/{run}/hops.jsonl")
    src = f"runs/{run}/hops.jsonl"
    done = bool(rows) and rows[-1].get("finish") == "STOP"
    if not done:
        for f in ("visible", "hops", "minutes", "cost_usd", "seams_pass"):
            put(f"{prefix}.{f}", None, src, "run not finished", pending=True)
        return
    last = rows[-1]
    put(f"{prefix}.visible", last["visible_total"], src, "last row visible_total")
    put(f"{prefix}.hops", len(rows), src, "row count")
    put(f"{prefix}.minutes", round(last["t"] / 60, 1), src, "last row t / 60", raw=last["t"])
    vis = last["visible_total"]; thk = sum(r.get("thinking_hop") or 0 for r in rows)
    prompt = sum(r.get("prompt_hop") or 0 for r in rows)
    put(f"{prefix}.cost_usd", round((vis + thk) * 10 / 1e6 + prompt * 2 / 1e6, 2), src,
        "derived: $10/1M x (visible + thinking) + $2/1M x sum(prompt_hop); same formula as viewer/build_data.py",
        derived=True, prompt_tokens=prompt)
    seams = ROOT / f"reports/{run}_seams.json"
    if seams.exists():
        s = json.loads(seams.read_text())
        put(f"{prefix}.seams_pass", sum(x["status"] == "PASS" for x in s["seams"]), f"reports/{run}_seams.json", "count status PASS")
        put(f"{prefix}.seams_total", len(s["seams"]), f"reports/{run}_seams.json", "len(seams)")


hops("expansion", "exp1")
hops("expansion_v2", "exp2")

code = ROOT / "reports/expansion_code.json"
if code.exists():
    t = json.loads(code.read_text())["totals"]
    p = "reports/expansion_code.json"
    put("exp1.files", t["files"], p, "totals.files")
    put("exp1.edges", t["d2_edges"], p, "totals.d2_edges")
    put("exp1.edges_resolved", t["d2_resolved"], p, "totals.d2_resolved")
    put("exp1.calls_checked", t["d2_calls_checked"], p, "totals.d2_calls_checked")
    put("exp1.arity_mismatch", t["d2_arity_mismatch"], p, "totals.d2_arity_mismatch")
    put("exp1.tests", t["d4_tests"], p, "totals.d4_tests")
    put("exp1.tests_passed", t["d4_passed"], p, "totals.d4_passed")
    put("exp1.bad_literals_nontest", t["d3_bad_literals_nontest"], p, "totals.d3_bad_literals_nontest")


# --- matched packages: hidden acceptance tests (same tests for A and B)
def junit(name, suite):
    p = f"reports/{name}.xml"
    root = ET.parse(ROOT / p).getroot()
    n = f = 0
    for tc in root.iter("testcase"):
        if (tc.get("classname") or "").split(".")[-1] == suite:
            n += 1; f += tc.find("failure") is not None or tc.find("error") is not None
    put(f"accept.{name}.{suite}.tests", n, p, f"testcases in {suite}")
    put(f"accept.{name}.{suite}.passed", n - f, p, f"testcases in {suite} without failure/error")


for name, suite in [("accept_core", "test_rules"), ("accept_core", "test_allocate"), ("accept_core_patched", "test_rules"),
                    ("accept_b_rules", "test_rules"), ("accept_b_allocate", "test_allocate"), ("accept_b_route", "test_route")]:
    junit(name, suite)

# --- baselines README (C: RAG + LLM + code)
b = (ROOT / "baselines/README.md").read_text()
m = re.search(r"\*\*C's LLM usage:\*\* (\d+) calls", b)
put("baseline_c.calls", int(m.group(1)), "baselines/README.md", "C's LLM usage calls")
m = re.search(r"est\. \*\*\$([\d.]+)\*\*", b)
put("baseline_c.usd", float(m.group(1)), "baselines/README.md", "C est. cost")
for name in ("baseline_c", "baseline_d"):
    r = jload(f"reports/{name}_plan.json")
    put(f"{name}.hard_errors", r["hard_errors"], f"reports/{name}_plan.json", "hard_errors")
    put(f"{name}.recall", round(r["classification"]["recall"], 3), f"reports/{name}_plan.json", "classification.recall")

if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent / "numbers.json"
    out.write_text(json.dumps(N, indent=1) + "\n")
    print(f"{len(N)} numbers -> {out}; pending: {[k for k, v in N.items() if v.get('pending')]}")
