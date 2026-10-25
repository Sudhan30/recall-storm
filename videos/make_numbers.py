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

def code_report(run, prefix):
    code = ROOT / f"reports/{run}_code.json"
    if not code.exists():
        for f in ("edges", "files_manifest", "longest_def.start_tok", "longest_use.start_tok", "b0.files_failed", "b1.files_failed",
                  "bad_literals_nontest"):
            put(f"{prefix}.{f}", None, f"reports/{run}_code.json", "report not written yet", pending=True)
        return
    full = json.loads(code.read_text())
    t = full["totals"]
    p = f"reports/{run}_code.json"
    put(f"{prefix}.files", t["files"], p, "totals.files")
    put(f"{prefix}.files_manifest", t["manifest_files_present"], p, "totals.manifest_files_present (files the stream wrote)")
    put(f"{prefix}.edges", t["d2_edges"], p, "totals.d2_edges")
    put(f"{prefix}.edges_resolved", t["d2_resolved"], p, "totals.d2_resolved")
    put(f"{prefix}.calls_checked", t["d2_calls_checked"], p, "totals.d2_calls_checked")
    put(f"{prefix}.arity_mismatch", t["d2_arity_mismatch"], p, "totals.d2_arity_mismatch")
    put(f"{prefix}.tests", t["d4_tests"], p, "totals.d4_tests")
    put(f"{prefix}.tests_passed", t["d4_passed"], p, "totals.d4_passed")
    put(f"{prefix}.bad_literals_nontest", t["d3_bad_literals_nontest"], p, "totals.d3_bad_literals_nontest")
    put(f"{prefix}.max_tok", t["max_tok"], p, "totals.max_tok")
    for b, key in (("0-200K", "b0"), ("200-400K", "b1")):
        bk = full["buckets"]["position"].get(b, {})
        put(f"{prefix}.{key}.files", bk.get("files"), p, f"buckets.position.{b}.files")
        put(f"{prefix}.{key}.files_failed", bk.get("d4_files_failed"), p, f"buckets.position.{b}.d4_files_failed")
    # The longest passing call shown on the code wall. v1 values are the files the viewer's "Longest passing
    # cross-file call" button opened; for v2, edit LONGEST below after looking at the v2 code wall.
    byp = {f["path"]: f for f in full["files"]}
    for key, path in LONGEST.get(run, ()):
        if path in byp:
            put(f"{prefix}.{key}.start_tok", byp[path]["start_tok"], p, f"files[{path}].start_tok")
        else:
            put(f"{prefix}.{key}.start_tok", None, p, f"{path} not in report", pending=True)


LONGEST = {"expansion": (("longest_def", "recallstorm/core/ids.py"),
                         ("longest_use", "tests/integration/test_flow_10_exceptions_and_handoffs.py")),
           "expansion_v2": ()}          # fill in from the v2 code wall
code_report("expansion", "exp1")
code_report("expansion_v2", "exp2")

# live test run shown in the code-wall beat (real capture, not one of the report files)
tl = (ROOT / "videos/assets/term/exp_longest_test.txt")
if tl.exists():
    m = re.search(r"(\d+) passed", tl.read_text())
    put("live.longest_tests_passed", int(m.group(1)), "videos/assets/term/exp_longest_test.txt",
        "live pytest run captured 2026-10-25 (real terminal output)", live=True)


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


# --- plain-language numbers (team lead, 12:35): store-manager phrasing, each phrase mapped to its sources
stores_all = [l for l in (ROOT / "data/stores_all.jsonl").read_text().splitlines() if l.strip()]
put("stores_all.ca", len(stores_all), "data/stores_all.jsonl", "line count (all CA); spoken as 'nearly 300'")
for name in ("core_patched", "core"):
    p = f"reports/{name}_plan.json"; r = jload(p); c = r["classification"]
    put(f"{name}.tp", c["tp"], p, "classification.tp (products with Red No. 3 found)")
    put(f"{name}.fp", c["fp"], p, "classification.fp (extra pulls)")
    put(f"{name}.truth_pull", c["tp"] + c["fn"], p, "classification.tp + fn (products that contain Red No. 3)")
    put(f"{name}.uncovered_facings", r["coverage"]["pull_facings"] - r["coverage"]["pull_facings_tasked"], p,
        "coverage.pull_facings - pull_facings_tasked (shelf spots left with banned product)")
    put(f"{name}.labor_hard", r["by_check"].get("labor", {}).get("hard", 0), p, "by_check.labor.hard (double-booking etc.)")
    put(f"{name}.deadline_hard", r["by_check"].get("deadline", {}).get("hard", 0), p, "by_check.deadline.hard")
r = jload("reports/core_patched_plan.json")
put("core_patched.fp_truth_hold", r["classification"]["confusion"]["HOLD_VERIFY"].get("PULL", 0), "reports/core_patched_plan.json",
    "classification.confusion.HOLD_VERIFY.PULL (the extra pull is labeled 'check by hand')")
for name, key in (("expansion_plan", "exp1plan"), ("expansion_agentpatched_plan", "exp1fixed")):
    p = f"reports/{name}.json"
    if (ROOT / p).exists():
        r = jload(p)
        put(f"{key}.mistakes", r["hard_errors"], p, "hard_errors (spoken as 'plan mistakes')")
        put(f"{key}.labor", r["by_check"].get("labor", {}).get("hard", 0), p, "by_check.labor.hard (associate overlaps)")
for pre, run in (("exp1", "expansion"), ("exp2", "expansion_v2")):
    vis = N.get(f"{pre}.visible", {}).get("value")
    if vis:
        put(f"{pre}.visible_k", f"{round(vis / 1000):,},000", f"runs/{run}/hops.jsonl",
            "visible_total rounded to thousands", derived=True, raw=vis)
    else:
        put(f"{pre}.visible_k", None, f"runs/{run}/hops.jsonl", "run not finished", pending=True)
agent = {r["name"]: r for r in jl("patches/agent/LOG.jsonl")}
roots = [n for n in ("exp_aliases_detect_coverage_regraded", "exp_plan_tasks_labor") if n in agent]
put("agent.exp_root_causes", len(roots), "patches/agent/LOG.jsonl", f"expansion repairs applied: {roots}")
held = set()
for n in roots:
    dh = agent[n].get("drill_holdout") or {}
    if dh.get("held_after") == 0:
        held |= set(dh.get("held_stores", []))
put("agent.exp_heldout_stores", len(held), "patches/agent/LOG.jsonl", "drill_holdout.held_stores with held_after == 0")

PHRASES = {
    "nearly 300 California stores": ["stores_all.ca"],
    "the drill runs on 20 stores": ["core_patched.stores"],
    "Found all 467 products that contain Red No. 3": ["core_patched.tp", "core_patched.truth_pull"],
    "Pulled 0 of 483 look-alikes like Red 40": ["core_patched.decoys_pulled", "core_patched.decoys"],
    "1 extra item pulled that our rules mark as 'check by hand'": ["core_patched.fp", "core_patched.fp_truth_hold"],
    "Every one of 6,718 affected shelf spots has a pull task": ["core_patched.pull_facings", "core_patched.pull_facings_tasked"],
    "0 plan mistakes: nobody double-booked, every task finished before midnight":
        ["core_patched.hard_errors", "core_patched.labor_hard", "core_patched.deadline_hard"],
    "Argon's first draft missed 25 of the 467 products, leaving 350 shelf spots with banned product":
        ["core.fn", "core.truth_pull", "core.uncovered_facings"],
    "Three small fixes closed the gap": ["patches.core_count", "core_patched.fn", "core_patched.uncovered_facings"],
    "about 254,000 tokens of code in one continued generation": ["exp1.visible_k", "exp1.visible"],
    "Every file and every cross-file call lined up": ["exp1.edges", "exp1.edges_resolved", "exp1.arity_mismatch"],
    "314 files, and every one of its 2,838 cross-file links lines up": ["exp1.files_manifest", "exp1.edges", "exp1.edges_resolved"],
    "hundreds of products (467 contain Red No. 3)": ["core_patched.truth_pull"],
    "thousands of shelf spots (6,718 affected)": ["core_patched.pull_facings"],
    "7,632 of them: one associate booked in two places at once": ["exp1plan.labor"],
    "the plan had 8,441 mistakes, mostly the same associate booked for two shelves at once": ["exp1plan.mistakes", "exp1plan.labor"],
    "the managed agent found the two root causes, fixed them, and the mistakes went to 0":
        ["agent.exp_root_causes", "exp1fixed.mistakes"],
    "including in 10 stores it never saw": ["agent.exp_heldout_stores"],
}

if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent / "numbers.json"
    out.write_text(json.dumps(N, indent=1) + "\n")
    ph = {k: [{"key": x, **N[x]} for x in v] for k, v in PHRASES.items()}
    (out.parent / "numbers_phrases.json").write_text(json.dumps(ph, indent=1) + "\n")
    print(f"{len(N)} numbers -> {out}; pending: {[k for k, v in N.items() if v.get('pending')]}")
