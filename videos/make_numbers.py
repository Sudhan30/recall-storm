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

cmp_p = ROOT / "viewer/data/compare.json"
if cmp_p.exists():
    cmp_all = json.loads(cmp_p.read_text())
    cmp = cmp_all.get("v1", cmp_all)
    v2c = cmp_all.get("v2")
    if v2c:
        for side, key in (("left", "exp2plan"), ("right", "exp2fixed")):
            for f, desc in (("overlaps", "double-bookings"), ("outside", "tasks outside the 10 PM-6 AM shift")):
                put(f"{key}.{f}", v2c[side][f], "viewer/data/compare.json", f"v2.{side}.{f} ({desc}; {v2c[side]['name']})")
            sid = next(iter(v2c[side]["stores"]))
            put(f"{key}.overlaps_shown_store", (v2c[side].get("stores") or {}).get(sid, {}).get("overlaps") if sid else None,
                "viewer/data/compare.json", f"v2.{side}.stores[first].overlaps: on screen in compare_both_v2 (not spoken)")
    for side, key in (("left", "exp1plan"), ("right", "exp1fixed")):
        put(f"{key}.double_bookings", sum(st["overlaps"] for st in cmp[side]["stores"].values()), "viewer/data/compare.json",
            f"sum of {side}.stores[*].overlaps (viewer/build_compare.py: verify_plan's labor overlap rule on "
            f"out/{'expansion' if side == 'left' else 'expansion_agentpatched'}/plan.jsonl); cross-check: "
            f"reports/expansion_plan.json by_check.labor.hard = 7,632 includes 1 over-shift-minutes error")
        put(f"{key}.double_booking_stores", len(cmp[side]["stores"]), "viewer/data/compare.json", f"len({side}.stores)")
        sid = next(iter(cmp[side]["stores"]))
        put(f"{key}.double_bookings_shown_store", cmp[side]["stores"][sid]["overlaps"], "viewer/data/compare.json",
            f"{side}.stores[first].overlaps: on screen in the compare capture (not spoken; store ID not shown)")


# --- expansion v2 (final, 2026-10-25 ~1:45 PM): unedited vs v2 + agent patches
def _v2():
    sc = (ROOT / "reports/expansion_v2_score.txt")
    if not sc.exists():
        return
    rows = jl("runs/expansion_v2/hops.jsonl")
    put("exp2.context_last_hop", rows[-1]["prompt_hop"], "runs/expansion_v2/hops.jsonl", "last row prompt_hop (context read by the last hop)")
    put("exp2.input_total", sum(r["prompt_hop"] for r in rows), "runs/expansion_v2/hops.jsonl", "sum(prompt_hop); = 'input 3,537,080' in reports/expansion_v2_score.txt")
    u = json.loads((ROOT / "reports/expansion_v2_code.json").read_text())
    t = u["totals"]; p = "reports/expansion_v2_code.json"
    put("exp2u.py_files", t["files"], p, "totals.files"); put("exp2u.py_parsed", t["parsed"], p, "totals.parsed")
    put("exp2u.test_files", t["d4_files"], p, "totals.d4_files")
    put("exp2u.test_files_noload", t["d4_by_status"].get("collection_error", 0), p, "totals.d4_by_status.collection_error")
    bad = [e for e in u["parse_errors"] if e["path"] == "recallstorm/aliases/translations.py"]
    put("exp2u.badline_tok", next(f["start_tok"] for f in u["files"] if f["path"] == "recallstorm/aliases/translations.py"),
        p, "files[recallstorm/aliases/translations.py].start_tok (file with the mis-indented line)", parse_error=bad[0] if bad else None)
    a = json.loads((ROOT / "reports/expansion_v2_agentpatched_code.json").read_text())
    t = a["totals"]; p = "reports/expansion_v2_agentpatched_code.json"
    put("exp2.files_manifest", t["manifest_files_present"], p, "totals.manifest_files_present (911/911 manifest files emitted)")
    put("exp2.edges", t["d2_edges"], p, "totals.d2_edges (after the one-line fix)")
    put("exp2.edges_resolved", t["d2_resolved"], p, "totals.d2_resolved")
    put("exp2.calls_checked", t["d2_calls_checked"], p, "totals.d2_calls_checked")
    put("exp2.arity_mismatch", t["d2_arity_mismatch"], p, "totals.d2_arity_mismatch")
    put("exp2.names", sum(b.get("d1_symbols", 0) for b in a["buckets"]["position"].values()), p, "sum buckets.position.*.d1_symbols")
    put("exp2.names_ok", sum(b.get("d1_ok", 0) for b in a["buckets"]["position"].values()), p, "sum buckets.position.*.d1_ok")
    put("exp2.test_files", t["d4_files"], p, "totals.d4_files")
    put("exp2.test_files_pass", t["d4_by_status"].get("passed", 0), p, "totals.d4_by_status.passed")
    dep = [json.loads(l) for l in (ROOT / "reports/expansion_v2_agentpatched_deps.jsonl").read_text().splitlines()
           if '"make_run_id"' in l and "test_flow_09_analytics_governance" in l]
    if dep:
        put("exp2.longest_def.start_tok", dep[0]["def_tok"], "reports/expansion_v2_agentpatched_deps.jsonl", "make_run_id def_tok")
        put("exp2.longest_use.start_tok", dep[0]["use_tok"], "reports/expansion_v2_agentpatched_deps.jsonl", "test_flow_09 use_tok")
        put("exp2.longest_distance", dep[0]["distance"], "reports/expansion_v2_agentpatched_deps.jsonl", "distance")
    ag = {r["name"]: r for r in jl("patches/agent/LOG.jsonl")}
    fx = ag.get("v2_aliases_translations_regraded")
    if fx:
        put("agent.v2_fix1_secs", round(fx["secs"]), "patches/agent/LOG.jsonl", "v2_aliases_translations_regraded.secs", raw=fx["secs"])
    lb = ag.get("v2_plan_tasks_labor")
    if lb:
        L = "patches/agent/LOG.jsonl"
        put("exp2plan.mistakes", lb["drill_before"]["hard"], L, "v2_plan_tasks_labor.drill_before.hard (drill with the one-line fix)")
        put("exp2plan.labor", lb["drill_before"]["by_check"]["labor"]["hard"], L, "v2_plan_tasks_labor.drill_before.by_check.labor.hard")
        put("exp2fixed.labor", lb["drill_after"]["by_check"].get("labor", {}).get("hard", 0), L, "drill_after.by_check.labor.hard")
        dh = lb["drill_holdout"]
        put("exp2.heldout_before", dh["held_before"], L, "v2_plan_tasks_labor.drill_holdout.held_before")
        put("exp2.heldout_after", dh["held_after"], L, "v2_plan_tasks_labor.drill_holdout.held_after")
        put("exp2.heldout_stores", len(dh["held_stores"]), L, "len(drill_holdout.held_stores)")
    db = ROOT / "runs/repair_v2_plan_tasks_labor/drill_before/plan_report.json"
    if db.exists():
        put("exp2plan.mistakes_report", json.loads(db.read_text())["hard_errors"], str(db.relative_to(ROOT)),
            "hard_errors (cross-check of the LOG.jsonl drill_before)")
    r = jload("reports/expansion_v2_agentpatched_plan.json"); p = "reports/expansion_v2_agentpatched_plan.json"
    c = r["classification"]
    put("exp2fixed.mistakes", r["hard_errors"], p, "hard_errors (final v2 plan mistakes)")
    put("exp2fixed.missed_spots", r["by_check"].get("coverage", {}).get("hard", 0), p, "by_check.coverage.hard")
    put("exp2fixed.decoys_pulled", c["decoys_pulled"], p, "classification.decoys_pulled")
    put("exp2fixed.found", c["tp"], p, "classification.tp"); put("exp2fixed.missed", c["fn"], p, "classification.fn")
    put("exp2fixed.truth_pull", c["tp"] + c["fn"], p, "classification.tp + fn")


_v2()

PHRASES = {
    "Each row is one simulated associate. Red means Argon's plan sent the same person to two shelves at once: "
    "7,631 double-bookings across 20 stores": ["exp1plan.double_bookings", "exp1plan.double_booking_stores"],
    "after the agent's fixes: 0 double-bookings": ["exp1fixed.double_bookings"],
    "646,825 tokens of code, 911 files, over 10 hops": ["exp2.visible", "exp2.files_manifest", "exp2.hops"],
    "every one of its 6,581 cross-file links lines up after a single one-line fix":
        ["exp2.edges", "exp2.edges_resolved", "exp2u.py_parsed", "exp2u.py_files", "exp2u.badline_tok"],
    "after a one-line fix the agent made in 21 seconds (one mis-indented line)": ["agent.v2_fix1_secs", "exp2u.badline_tok"],
    "The rest, 12 missed products and 3 look-alikes, are still open": ["exp2fixed.missed", "exp2fixed.decoys_pulled", "exp2fixed.missed_spots"],
    "a test written at token 641,687 calls a function written 552,084 tokens earlier":
        ["exp2.longest_use.start_tok", "exp2.longest_distance", "exp2.longest_def.start_tok"],
    "all 9 hand-offs between hops came out clean": ["exp2.seams_pass", "exp2.seams_total"],
    "Our verifier ran the plan and found 21,459 mistakes, 21,284 of them in scheduling":
        ["exp2plan.mistakes", "exp2plan.mistakes_report", "exp2plan.labor"],
    "7,161 times the plan sent someone to two shelves at once, and 14,117 tasks fell outside the 10 PM to 6 AM shift":
        ["exp2plan.overlaps", "exp2plan.outside"],
    "the root cause: one shared time cursor for all associates": ["agent.v2_plan_tasks_labor.result"],
    "scheduling mistakes went from 21,284 to 0, even in 10 stores it never saw":
        ["exp2plan.labor", "exp2fixed.labor", "exp2.heldout_before", "exp2.heldout_after", "exp2.heldout_stores"],
    "Plan mistakes went from 21,459 to 175: 12 missed products and 3 look-alikes, still open":
        ["exp2plan.mistakes", "exp2fixed.mistakes", "exp2fixed.missed", "exp2fixed.missed_spots", "exp2fixed.decoys_pulled"],
    "plan mistakes from 21,459 to 175": ["exp2plan.mistakes", "exp2fixed.mistakes"],
    "In that run, our verifier found 21,459 plan mistakes, mostly one associate sent to two shelves at once, or outside their shift":
        ["exp2plan.mistakes", "exp2plan.labor", "exp2plan.overlaps", "exp2plan.outside", "exp2plan.mistakes_report"],
    "A managed agent fixed the root cause: scheduling mistakes went to zero, even in 10 stores it never saw":
        ["exp2fixed.labor", "exp2.heldout_before", "exp2.heldout_after", "exp2.heldout_stores"],
    "scheduling mistakes to 0, including in 10 stores it never saw":
        ["exp2plan.labor", "exp2fixed.labor", "exp2.heldout_before", "exp2.heldout_after", "exp2.heldout_stores"],
    "Large run: the same fix loop (bars card)": ["exp2plan.mistakes", "exp2fixed.mistakes", "exp2plan.labor", "exp2fixed.labor",
        "exp2plan.overlaps", "exp2plan.outside", "exp2fixed.missed_spots", "exp2fixed.decoys_pulled", "exp2.heldout_stores"],
    "the 175 left: 172 shelf spots from 12 missed products, and 3 look-alikes":
        ["exp2fixed.mistakes", "exp2fixed.missed_spots", "exp2fixed.missed", "exp2fixed.decoys_pulled"],
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
    "7,631 double-bookings: one associate in two places at once (card)": ["exp1plan.double_bookings", "exp1plan.labor"],
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
