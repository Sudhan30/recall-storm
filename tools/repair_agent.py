"""OURS. Repair loop: send one failure bundle to the Antigravity managed agent, verify its patch locally.

Usage:
  python tools/repair_agent.py NAME --gen gen/core --file recallstorm/plan/planner.py \
      --tests acceptance/test_route.py [--unit tests/unit/test_plan_planner.py] \
      [--shim recallstorm.route=recallstorm.plan.planner:pack_returns] [--max-tokens 300000] [--minutes 15]

The agent sees only the bundle: the failing file, its manifest entry, the signatures it imports, and the test
output. It never sees hidden test source or the rest of the generation. Scores come from our local re-run,
not from the agent's report. Writes patches/agent/NAME.patch, runs/repair_NAME/, patches/agent/LOG.jsonl.
"""
import argparse, ast, difflib, json, pathlib, re, shutil, subprocess, sys, time
from google import genai

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "runs"  # gitignored
AGENT = "antigravity-preview-05-2026"

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("--gen", required=True)
ap.add_argument("--file", required=True)
ap.add_argument("--tests", nargs="*", default=[])
ap.add_argument("--drill-check", help="evidence = verify_plan errors of this check (e.g. labor) from a drill run")
ap.add_argument("--lots-mode", help="score on the fda_lots scenario instead: scenarios/fda_lots/adapter.py --mode M, "
                                     "then tools/verify_lots.py; hold-out is by recall notice")
ap.add_argument("--exclude-basis", nargs="*", default=[], help="lots mode: drop coverage errors of these label bases "
                                                                "from the evidence and score (e.g. date_window)")
ap.add_argument("--unit", nargs="*", default=[])
ap.add_argument("--shim", action="append", default=[])
ap.add_argument("--max-tokens", type=int, default=300_000)
ap.add_argument("--minutes", type=float, default=15)
ap.add_argument("--holdout", action="store_true",
                help="hide every other failing test from the bundle; score seen and held-out failures separately")
ap.add_argument("--start-patch", help="apply this patch to the file first (a later repair round)")
ap.add_argument("--guards", type=int, default=0,
                help="add N passing labeled SKUs (generic-color boundary, stratified by truth) as must-still-pass cases")
ap.add_argument("--attach", help="listen on an existing interaction id instead of creating one (after a client timeout)")
ap.add_argument("--dry-run", action="store_true", help="build the bundle and run tests, skip the agent")
a = ap.parse_args()

run = SCRATCH / f"repair_{a.name}"
if run.exists():
    shutil.rmtree(run)
run.mkdir(parents=True)
gen = ROOT / a.gen
work = run / "work"
shutil.copytree(gen, work)
if a.start_patch:
    subprocess.run(["patch", "-s", "-p1", "-d", str(work)], stdin=open(ROOT / a.start_patch), check=True)


def add_shims(base: pathlib.Path):
    for s in a.shim:                                  # recallstorm.route=recallstorm.plan.planner:pack_returns
        mod, target = s.split("=")
        tmod, name = target.split(":")
        p = base / pathlib.Path(*mod.split(".")) / "__init__.py"
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f'"""OURS. Test shim exposing {target} as {mod}.{name}."""\nfrom {tmod} import {name}\n')


def run_lots(base: pathlib.Path, tag: str) -> dict:
    """Run v1-style generated code on the fda_lots scenario via our adapter, score with verify_lots."""
    out = run / f"lots_{tag}"
    env = {"PATH": "/usr/bin:/bin", "RECALLSTORM_GEN": str(base), "PYTHONPATH": str(ROOT)}
    r = subprocess.run([sys.executable, str(ROOT / "scenarios" / "fda_lots" / "adapter.py"), "--mode", a.lots_mode,
                        "--out", str(out)], capture_output=True, text=True, env=env, cwd=ROOT, timeout=900)
    if r.returncode != 0 or not (out / "plan.jsonl").exists():
        return {"crash": (r.stderr or r.stdout)[-3000:], "by_check": {}, "errors": []}
    rep_path = out / "lots_report.json"
    subprocess.run([sys.executable, str(ROOT / "tools" / "verify_lots.py"), str(out / "plan.jsonl"), "--report",
                    str(rep_path), "--quiet"], capture_output=True, text=True, cwd=ROOT, timeout=900,
                   env={**env, "VERIFY_PLAN_MAX_EXAMPLES": "1000000"})
    rp = json.loads(rep_path.read_text())
    errs = [e for e in rp.get("errors", []) if e.get("severity") == "hard"
            and not any(f"basis {b}" in e.get("msg", "") for b in a.exclude_basis)]
    by_check = {}
    for e in errs:
        by_check[e["check"]] = by_check.get(e["check"], 0) + 1
    return {"by_check": by_check, "hard": len(errs), "errors": errs, "lots": rp.get("lots")}


def run_drill(base: pathlib.Path, tag: str) -> dict:
    """Run the drill on the real pack with this work dir, verify it, return error counts and samples."""
    if a.lots_mode:
        return run_lots(base, tag)
    out = run / f"drill_{tag}"
    env = {"PYTHONPATH": f"{base}:{ROOT}", "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, "-m", "recallstorm", "run", "--scenario", "ca_red3", "--data", str(ROOT / "data"),
                        "--out", str(out)], capture_output=True, text=True, env=env, cwd=ROOT, timeout=600)
    if r.returncode != 0:
        return {"crash": r.stderr[-3000:], "by_check": {}, "errors": []}
    rep_path = out / "plan_report.json"
    subprocess.run([sys.executable, str(ROOT / "tools" / "verify_plan.py"), str(out / "plan.jsonl"), "--labels",
                    str(ROOT / "data" / "labels.csv"), "--data", str(ROOT / "data"), "--report", str(rep_path)],
                   capture_output=True, text=True, cwd=ROOT, timeout=600,
                   env={**env, "PYTHONPATH": str(ROOT), "VERIFY_PLAN_MAX_EXAMPLES": "1000000"})
    rp = json.loads(rep_path.read_text())
    errs = [e for e in rp.get("errors", []) if e.get("severity") == "hard"]
    by_check = {}
    for e in errs:
        by_check[e["check"]] = by_check.get(e["check"], 0) + 1
    return {"by_check": rp.get("by_check") or by_check, "hard": rp.get("hard_errors"), "errors": errs}


def store_of(e: dict) -> str:
    txt = (e.get("id") or "") + " " + (e.get("msg") or "")
    if a.lots_mode:                                   # hold out whole recall notices, not stores
        m = re.search(r"recall ([A-Z]-\d{4}-\d{4})", txt)
        if m:
            return m.group(1)
        m = re.search(r"\bFDA([A-Z])(\d{4})(\d{4})\b", txt)       # simulated SKU id FDAF02642025 -> F-0264-2025
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "?"
    m = re.search(r"TSK-([A-Z0-9]+)-", txt) or re.search(r"\bat ([A-Z]+\d+)\b", txt)
    return m.group(1) if m else "?"


CHECK_RULES = {
    "labor": "an associate may not have two tasks whose windows overlap; every window must lie inside that associate's "
             "shift and end before the scenario deadline.",
    "coverage": "every SKU whose label contains FD&C Red No. 3 under any alias in the rules (including spacing, "
                "punctuation, '#', OCR digit-for-letter noise and non-English names) must get a PULL verdict, so every "
                "shelf facing of it gets a PULL task.",
    "lots": "",
    "decoy": "a SKU must not be pulled when its label only names a different dye (Red 40, D&C Red 33) or a phrase like "
             "'3 red apples'.",
}


def hide_tests(output: str, held: tuple[str, ...]) -> str:
    """Drop held-out tests' traceback sections, FAILED lines and the counts line from pytest output."""
    names = {h.split("::", 1)[1] for h in held}
    keep, skipping = [], False
    for line in output.splitlines():
        sec = re.match(r"^_{3,} (.+?) _{3,}$", line)
        if sec:
            skipping = sec.group(1) in names
        if re.match(r"^=+ short test summary", line) or re.match(r"^=+ \d+ (failed|passed)", line):
            skipping = False
        if skipping or (line.startswith("FAILED ") and re.sub(r" - .*$", "", line[7:]).split("::", 1)[-1] in names):
            continue
        if re.match(r"^=+ \d+ (failed|passed)", line):
            continue
        keep.append(line)
    return "\n".join(keep)


def run_tests(base: pathlib.Path, files: list[str]) -> dict:
    files = [str((ROOT / f) if f.startswith("acceptance") else (base / f)) for f in files]
    env = {"PYTHONPATH": f"{base}:{ROOT}", "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, "-m", "pytest", *files, "-q", "--no-header", "-p", "no:cacheprovider",
                        "--tb=short", "-rf"], capture_output=True, text=True, env=env,
                       cwd=base, timeout=300)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
    m = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|error|errors|skipped)", tail)}
    return {"summary": tail, "passed": m.get("passed", 0), "failed": m.get("failed", 0) + m.get("error", 0)
            + m.get("errors", 0), "output": r.stdout,
            "failed_ids": sorted(set(re.findall(r"^FAILED (.+?::.+?)(?: - .*)?$", r.stdout, re.M)))}


def imported_signatures(src: str, base: pathlib.Path) -> str:
    """Public def/class signature lines of every local module the failing file imports."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
            cands = [base / pathlib.Path(*mod.split(".")).with_suffix(".py"),
                     base / pathlib.Path(*mod.split(".")) / "__init__.py", ROOT / f"{mod}.py"]
            for c in cands:
                if c.exists():
                    names = {al.name for al in node.names}
                    t = c.read_text()
                    for d in ast.parse(t).body:
                        if isinstance(d, (ast.FunctionDef, ast.ClassDef)) and d.name in names:
                            seg = ast.get_source_segment(t, d) or ""
                            head = seg.split(":\n")[0] if isinstance(d, ast.FunctionDef) else seg[:1500]
                            out.append(f"# from {mod}\n{head}")
                    break
    return "\n\n".join(out)


add_shims(work)
before = run_tests(work, a.tests) if a.tests else {"summary": "no tests", "passed": 0, "failed": 0, "output": "",
                                                  "failed_ids": []}
drill_before = run_drill(work, "before") if a.drill_check else None
drill_shown_txt, held_stores = "", set()
if drill_before:
    errs = [e for e in drill_before["errors"] if e["check"] == a.drill_check]
    stores = sorted({store_of(e) for e in errs})
    held_stores = set(stores[1::2]) if a.holdout else set()
    shown = [e for e in errs if store_of(e) not in held_stores]
    drill_shown_txt = (f"verify_plan hard errors of check '{a.drill_check}' on the drill output "
                       f"({len(shown)} shown, from {len(stores) - len(held_stores)} stores; other stores hidden):\n" +
                       "\n".join(f"- [{e['src']}] {e['type']} {e['id']}: {e['msg']}" for e in shown[:60]) +
                       "\n\nThe verifier rule: " + (
                           "every shelf lot covered by a recall notice's lot codes, lot ranges or 'all lots' wording "
                           "(case, punctuation and a 'LOT ' prefix do not matter) must get a PULL task; lots the "
                           "notice does not cover must not be pulled. Example notices follow."
                           if a.lots_mode else CHECK_RULES.get(a.drill_check, "see the error messages.")))
    if a.lots_mode:
        notices = [json.loads(l) for l in open(ROOT / "data" / "recalls_fda.jsonl")]
        shown_ids = {store_of(e) for e in shown}
        ex = [n for n in notices if n.get("recall_number") in shown_ids][:12]
        drill_shown_txt += "\n" + "\n".join(f"- {n['recall_number']}: code_info = {n.get('code_info', '')[:500]!r}" for n in ex)
held = tuple(before["failed_ids"][1::2]) if a.holdout else ()
shown_output = hide_tests(before["output"], held)[-20000:]
before_unit = run_tests(work, a.unit) if a.unit else None
src = (work / a.file).read_text()


def guard_cases(n: int, failing: set[str]) -> str:
    """Passing labeled SKUs near the generic-color boundary, n split evenly across truth labels."""
    import csv, random
    labels = dict(list(csv.reader(open(ROOT / "data" / "labels.csv")))[1:])
    skus = {json.loads(l)["sku_id"]: json.loads(l) for l in open(ROOT / "data" / "skus.jsonl")}
    generic = re.compile(r"artificial(?:ly)? colou?r|colou?rs? added|certified colou?r|fd&c colou?r", re.I)
    pool = {}
    for sid, truth in sorted(labels.items()):
        if sid in failing or sid not in skus or not generic.search(skus[sid]["ingredients"]):
            continue
        pool.setdefault(truth, []).append(sid)
    rng, out = random.Random(418), []
    for truth in sorted(pool):
        for sid in rng.sample(pool[truth], min(len(pool[truth]), n // len(pool))):
            sk = skus[sid]
            out.append(f"- expected {truth} | food={sk['is_food']} drug={sk['is_ingested_drug']} | {sk['ingredients'][:400]}")
    return "\n".join(out)


failing_skus = {m for t in before["failed_ids"] for m in re.findall(r"\[(\w+)\]", t)}
guards = guard_cases(a.guards, failing_skus) if a.guards else ""
manifest = next((l for l in (gen / "manifest.jsonl").read_text().splitlines() if f'"{a.file}"' in l), "{}")
bundle = f"""You are repairing ONE file of a Python package written by another model. Find the root cause of the
failing tests below and fix it in this file only. Keep every public name and signature unchanged; do not add
new dependencies (standard library only). Do not weaken behaviour to make tests pass.

Reply with exactly two parts and nothing else:
DIAGNOSIS: <one line: the root cause>
<<<FILE path={a.file}>>>
<the complete corrected file>
<<<END FILE>>>

=== manifest entry ===
{manifest}

=== signatures this file imports ===
{imported_signatures(src, work)}

{"=== currently PASSING cases that must still pass after your fix (state=CA, at the deadline) ===" + chr(10) + guards + chr(10) if guards else ""}
=== failing test output (test source is hidden) ===
{shown_output}
{drill_shown_txt}

=== {a.file} ===
{src}
"""
(run / "bundle.txt").write_text(bundle)
print(f"bundle {len(bundle)} chars (~{len(bundle)//4} tokens); before: {before['summary']}", flush=True)
if a.dry_run:
    sys.exit(0)

client = genai.Client()
ev = open(run / "events.jsonl", "a")
text, t0, iid, last_id, usage, status = [], time.time(), a.attach, None, None, None
stream = client.interactions.get(a.attach, stream=True) if a.attach else client.interactions.create(
    agent=AGENT, agent_config={"type": "antigravity", "model": "gemini-4-argon", "max_total_tokens": a.max_tokens},
    environment={"type": "remote", "network": "disabled"},  # sandbox, no egress: the bundle is all it gets
    input=bundle, background=True, stream=True)
done = False
while not done:
    try:
        for e in stream:
            et = getattr(e, "event_type", None)
            last_id = getattr(e, "event_id", None) or last_id
            rec = {"t": round(time.time() - t0, 1), "type": et}
            if et == "interaction.created":
                iid = e.interaction.id; rec["id"] = iid
            elif et == "step.delta" and getattr(e.delta, "type", None) == "text":
                text.append(e.delta.text); rec["chars"] = len(e.delta.text)
            elif et == "interaction.status_update":
                status = e.status; usage = e.usage.model_dump() if e.usage else usage; rec["status"] = status
            elif et in ("interaction.completed", "error"):
                rec["detail"] = str(e)[:400]; done = True
            ev.write(json.dumps(rec, default=str) + "\n"); ev.flush()
            if time.time() - t0 > a.minutes * 60:
                rec = {"t": round(time.time() - t0, 1), "type": "timeout"}; ev.write(json.dumps(rec) + "\n")
                done = True
            if done:
                break
        else:
            done = True
    except Exception as err:
        ev.write(json.dumps({"t": round(time.time() - t0, 1), "reconnect": repr(err)[:200]}) + "\n"); ev.flush()
        if not iid or time.time() - t0 > a.minutes * 60:
            raise
        time.sleep(5)
        stream = client.interactions.get(iid, stream=True, last_event_id=last_id)

final = client.interactions.get(iid) if iid else None
if final is not None:
    (run / "final.json").write_text(final.model_dump_json(indent=2))
    usage = final.usage.model_dump() if getattr(final, "usage", None) else usage
    status = final.status
reply = "".join(text) or (getattr(final, "output_text", None) or "" if final is not None else "")
(run / "reply.txt").write_text(reply)
diag = (re.search(r"DIAGNOSIS:\s*(.+)", reply) or [None, ""])[1].strip()
m = re.search(r"<<<FILE path=[^>]*>>>\n(.*?)<<<END FILE>>>", reply, re.S)
entry = {"name": a.name, "gen": a.gen, "file": a.file, "agent": AGENT, "status": status, "diagnosis": diag,
         "secs": round(time.time() - t0, 1), "usage": usage, "bundle_chars": len(bundle),
         "before": {k: before[k] for k in ("summary", "passed", "failed")},
         "drill_before": drill_before and {"hard": drill_before.get("hard"), "by_check": drill_before["by_check"],
                                            "crash": drill_before.get("crash")},
         "before_unit": before_unit and {k: before_unit[k] for k in ("summary", "passed", "failed")}}
if not m:
    entry["result"] = "NO_PATCH"
else:
    new = m.group(1)
    (work / a.file).write_text(new)
    after = run_tests(work, a.tests) if a.tests else dict(before)
    if a.drill_check:
        da = run_drill(work, "after")
        cnt = lambda errs, held: sum(1 for e in errs if e["check"] == a.drill_check and (store_of(e) in held_stores) == held)
        entry["drill_after"] = {"hard": da.get("hard"), "by_check": da["by_check"], "crash": da.get("crash")}
        entry["drill_holdout"] = {"shown_before": cnt(drill_before["errors"], False), "shown_after": cnt(da["errors"], False),
                                  "held_before": cnt(drill_before["errors"], True), "held_after": cnt(da["errors"], True),
                                  "held_stores": sorted(held_stores)}
        hard = lambda v: v.get("hard", 0) if isinstance(v, dict) else (v or 0)     # verify_plan: {"hard": n, "soft": m}
        bb = drill_before["by_check"] or {}
        worse = {k: {"before": hard(bb.get(k, 0)), "after": hard(v)} for k, v in (da["by_check"] or {}).items()
                 if hard(v) > hard(bb.get(k, 0))}
        entry["drill_regressions"] = worse
    still = set(after["failed_ids"])
    seen = [t for t in before["failed_ids"] if t not in held]
    entry["holdout"] = {"seen": len(seen), "seen_fixed": sum(t not in still for t in seen),
                        "held_out": len(held), "held_out_fixed": sum(t not in still for t in held),
                        "new_failures": sorted(still - set(before["failed_ids"]))}
    after_unit = run_tests(work, a.unit) if a.unit else None
    entry.update(after={k: after[k] for k in ("summary", "passed", "failed")},
                 after_unit=after_unit and {k: after_unit[k] for k in ("summary", "passed", "failed")},
                 result="FIXED" if after["failed"] == 0 and (not after_unit or after_unit["failed"] == 0)
                 else ("IMPROVED" if after["failed"] < before["failed"] else "NOT_FIXED"))
    if a.drill_check:
        dh, da_ = entry["drill_holdout"], entry["drill_after"]
        tot_b = dh["shown_before"] + dh["held_before"]; tot_a = dh["shown_after"] + dh["held_after"]
        ok_tests = not after_unit or after_unit["failed"] <= (before_unit or {}).get("failed", 0)
        entry["result"] = ("CRASH" if da_.get("crash") else "FIXED" if tot_a == 0 and not entry["drill_regressions"] and ok_tests
                           else "IMPROVED" if tot_a < tot_b and not entry["drill_regressions"] else "NOT_FIXED")
    pdir = ROOT / "patches" / "agent"; pdir.mkdir(parents=True, exist_ok=True)
    diff = difflib.unified_diff(src.splitlines(True), new.splitlines(True), f"a/{a.file}", f"b/{a.file}")
    (pdir / f"{a.name}.patch").write_text("".join(diff))
    entry["patch"] = f"patches/agent/{a.name}.patch"
with open(ROOT / "patches" / "agent" / "LOG.jsonl", "a") as f:
    f.write(json.dumps(entry, default=str) + "\n")
print(json.dumps(entry, indent=1, default=str))
