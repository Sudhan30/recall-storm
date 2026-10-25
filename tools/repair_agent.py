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
ap.add_argument("--tests", nargs="+", required=True)
ap.add_argument("--unit", nargs="*", default=[])
ap.add_argument("--shim", action="append", default=[])
ap.add_argument("--max-tokens", type=int, default=300_000)
ap.add_argument("--minutes", type=float, default=15)
ap.add_argument("--holdout", action="store_true",
                help="hide every other failing test from the bundle; score seen and held-out failures separately")
ap.add_argument("--start-patch", help="apply this patch to the file first (a later repair round)")
ap.add_argument("--guards", type=int, default=0,
                help="add N passing labeled SKUs (generic-color boundary, stratified by truth) as must-still-pass cases")
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
before = run_tests(work, a.tests)
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

=== {a.file} ===
{src}
"""
(run / "bundle.txt").write_text(bundle)
print(f"bundle {len(bundle)} chars (~{len(bundle)//4} tokens); before: {before['summary']}", flush=True)
if a.dry_run:
    sys.exit(0)

client = genai.Client()
ev = open(run / "events.jsonl", "a")
text, t0, iid, last_id, usage, status = [], time.time(), None, None, None, None
stream = client.interactions.create(
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
reply = "".join(text) or (final.model_dump_json() if final is not None else "")
(run / "reply.txt").write_text(reply)
diag = (re.search(r"DIAGNOSIS:\s*(.+)", reply) or [None, ""])[1].strip()
m = re.search(r"<<<FILE path=[^>]*>>>\n(.*?)<<<END FILE>>>", reply, re.S)
entry = {"name": a.name, "gen": a.gen, "file": a.file, "agent": AGENT, "status": status, "diagnosis": diag,
         "secs": round(time.time() - t0, 1), "usage": usage, "bundle_chars": len(bundle),
         "before": {k: before[k] for k in ("summary", "passed", "failed")},
         "before_unit": before_unit and {k: before_unit[k] for k in ("summary", "passed", "failed")}}
if not m:
    entry["result"] = "NO_PATCH"
else:
    new = m.group(1)
    (work / a.file).write_text(new)
    after = run_tests(work, a.tests)
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
    pdir = ROOT / "patches" / "agent"; pdir.mkdir(parents=True, exist_ok=True)
    diff = difflib.unified_diff(src.splitlines(True), new.splitlines(True), f"a/{a.file}", f"b/{a.file}")
    (pdir / f"{a.name}.patch").write_text("".join(diff))
    entry["patch"] = f"patches/agent/{a.name}.patch"
with open(ROOT / "patches" / "agent" / "LOG.jsonl", "a") as f:
    f.write(json.dumps(entry, default=str) + "\n")
print(json.dumps(entry, indent=1, default=str))
