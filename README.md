# Recall Storm

Gemini 4 Argon SF Hackathon, Track 1 (Million Token Engineering), Oct 25, 2026.

**In one minute.** On January 1, 2027, California bans food containing Red No. 3, with no sell-through period. We
asked Gemini 4 Argon to write the whole compliance system that clears it from store shelves overnight, then checked it.

- **One continued generation, 646,825 tokens:** 911 files over 10 hops, every seam clean. After one one-line fix
  by a managed agent, all 6,581 cross-file links resolve with zero argument mismatches. A test written at token
  641,687 calls a function written at token 89,603, and passes.
- **Consistent isn't correct:** our verifier ran that plan and found 21,459 mistakes, mostly people booked at two
  shelves at once or outside their shift. A managed agent found the root cause: scheduling mistakes went from 21,284
  to 0, including in stores it never saw, and the plan from 21,459 mistakes to 175.
- **A working system:** Argon's core, with three small logged fixes, finds all 467 products containing Red No. 3
  across a 20-store simulated drill, pulls none of the 483 look-alikes, and makes zero plan mistakes. `./demo.sh`
  runs it live in about 5 seconds.

Everything here was built at the event. Stores, stock and staffing are simulated; every number comes from the
verifier (`tools/`, `reports/`). Argon's output in `gen/` is unedited; every fix is in `patches/`, including the
attempts that failed.

A compliance drill for California AB 418 (FD&C Red No. 3 banned in food from 2027-01-01 00:00 local),
run across simulated store operations. Everything here was built at the event.

## Tiers

1. **Working core.** One Argon generation (`prompts/core.md`) writes `gen/core/recallstorm/`. We run it on a
   20-store pack and verify it. This powers the live demo.
2. **Experiment.** One continued Argon generation (`prompts/expansion.md`) writes a much larger version of the
   system. We verify every cross-file dependency by token range.
3. **Baseline B.** The same three packages (`rules`, `allocate`, `route`) written fresh in short calls,
   scored by the same hidden tests in `acceptance/`.

## Ownership

| Path | Owner |
|---|---|
| `contract.py`, `contract_io.py`, `prompts/`, `tools/`, `data/build_*.py`, `acceptance/`, `baselines/`, `viewer/` | OURS (written by the team today) |
| `gen/core/`, `gen/expansion/`, `gen/b/` | ARGON (model output, unedited) |
| `patches/` | Repair-loop patches, logged; never counted in Argon's token totals |

## What is real and what is simulated

- Real: rule text and dates (`data/build_rules.py`), product ingredient lists (USDA FoodData Central, CC0),
  store locations (see `data/build_stores.py` for source and license).
- Simulated (seeded, `data/build_sim.py`): DCs, districts, shelf facings, associates and shifts, trucks,
  DC stock, substitutes, store notes. Adversarial variants and decoys are ours.
- Every number in the demo comes from `tools/verify_code.py`, `tools/verify_plan.py`, or `acceptance/`.

## Results (every number from `reports/`, `runs/*/hops.jsonl` or `patches/`)

Simulated drill: a large big-box retailer's nearly 300 California store locations (286, OpenStreetMap); the drill runs
on 20 of them, overnight Dec 30-31, 2026, with 1,212 products (1,000 real USDA FoodData Central labels + 212 adversarial
variants and look-alikes we wrote). Ground truth: `data/labels.csv`. Hidden tests: `acceptance/` (never in any prompt).

### One continued generation

| Run | Visible tokens | Hops | Seams | Files | Cross-file references | Est. cost |
|---|---|---|---|---|---|---|
| Core (`gen/core`) | 22,523 | 1 | — | 18/18 | all resolve | — |
| Expansion v1 (`gen/expansion`) | 254,377 | 4 | 3/3 PASS | 314/314 (310 parse as code) | 2,838/2,838 resolve, 0 arity mismatches | ~$3.56 |
| Expansion v2 (`gen/expansion_v2`) | 646,825 | 10 | 9/9 PASS | 911/911 (904 of 907 `.py` parse) | 6,554/6,581 resolve, 0 arity mismatches in 4,862 calls | ~$13.54 |

Expansion v2 broke in one place: a single mis-indented line in `recallstorm/aliases/translations.py` (around
token 132,000) stops the label-reading package from importing, which takes down the drill, the hidden rules tests and
171 of v2's 663 test files. With the agent's one-line fix, all 6,581 cross-file references resolve (0 arity
mismatches in 4,881 calls), 2,326/2,326 promised names exist, and 656 of 663 test files pass. The longest passing
link: a test written at token 641,687 calls a function written at token 89,603. Hidden allocate (9/9) and route (7/7) tests pass because they don't import it.

Continuation was proven before the big runs: a 2-hop probe (`runs/probe/`, 32K-token seam) passed `tools/seam_check.py`.

### The drill (`tools/verify_plan.py`: missed shelves, double-booked associates, late tasks, stock, truck capacity, look-alikes pulled)

| Build | Plan mistakes (hard errors) | Red No. 3 products found | Look-alikes pulled | Hidden tests passed |
|---|---|---|---|---|
| Core, Argon's first draft (unedited) | 350 | 442 / 467 | 0 / 483 | 1,152 / 1,263 |
| Core + 3 small hand fixes (`patches/core/`) | **0** | **467 / 467** | 0 / 483 | 1,258 / 1,263 |
| Expansion v1, unedited | 8,441 | 411 / 467 | 3 / 483 | 1,194 / 1,270 |
| Expansion v1 + 3 managed-agent patches (`patches/agent/`) | **0** | **467 / 467** | 0 / 483 | 1,262 / 1,270 |
| Expansion v2, unedited | drill can't start (1 mis-indented line) | — | — | rules can't load; allocate 9/9, route 7/7 |
| Expansion v2 + 1-line agent fix | 21,459 | 455 / 467 | 3 / 483 | 1,238 / 1,270 |
| Expansion v2 + 2 agent patches (7 lines changed) | **175** | 455 / 467 | 3 / 483 | 1,238 / 1,270 |
| Baseline D: code only, written by us | 0 | 467 / 467 | 0 / 483 | 1,234 / 1,270 |
| Baseline C: retrieval + LLM + our code | 0 | 467 / 467 | 0 / 483 | 1,234 / 1,270 |

The core has no `route/` package, so its hidden route tests are skipped (1,263 instead of 1,270).

### Matched packages: written inside one long generation vs fresh short calls (same hidden tests)

| Package | Core (in-stream) | Expansion v1 (in-stream) | Expansion v2 + 1-line fix (in-stream) | Baseline B (fresh short call) |
|---|---|---|---|---|
| rules | 1,143 / 1,254 | 1,179 / 1,254 | 1,222 / 1,254 | 1,240 / 1,254 |
| allocate | 9 / 9 | 9 / 9 | 9 / 9 | 9 / 9 |
| route | — | 6 / 7 | 7 / 7 | 7 / 7 |

### Managed-agent repair loop (`tools/repair_agent.py`, Antigravity agent on gemini-4-argon, network disabled)

The agent sees one failing file plus the failures; half the failures (or half the stores / recall notices) are held
out of its bundle, and we re-score everything locally. Patches are never counted in Argon's token totals.

| Job | Result | Evidence |
|---|---|---|
| Core return packer (`plan/planner.py`) | FIXED | hidden route tests 6/7 → 7/7 |
| Baseline B rules, round 1 | NOT_FIXED | fixed 16/16 incl. 8/8 held out, but 32 new failures (over-corrected) |
| Baseline B rules, round 2 (with guard cases) | IMPROVED | 32 → 1 failing; 15/16 held-out fixed; 0 new |
| Expansion v1 scheduling (`plan/tasks.py`) | FIXED | double-bookings 7,632 → 0, incl. 3,759 → 0 in 10 stores it never saw |
| Expansion v1 label matching (`aliases/detect.py`) | IMPROVED | missed shelves 806 → 0 (381 → 0 in unseen stores); hidden tests 75 → 8 failing |
| Expansion v1 truck packing (`route/packing.py`) | FIXED | hidden route tests 6/7 → 7/7 |
| Expansion v1 lot parser (openFDA scenario) | NOT_FIXED | lot recall 0.20 → 0.40, but its unit tests regressed |
| Expansion v2 mis-indented line (`aliases/translations.py`) | FIXED | 21 s; rules tests un-loadable → 1,222/1,254; its 3 test files 0/3 → 3/3 |
| Expansion v2 scheduling (`plan/tasks.py`) | FIXED | scheduling mistakes 21,284 → 0 (7,161 double-bookings, 14,117 outside the shift), incl. 10,143 → 0 in unseen stores |
| Expansion v2 label matching (`aliases/detect.py`) | NOT_FIXED | look-alikes 3 → 0, but missed shelves 172 → 180 and 13 new test failures |

All attempts, including the failed ones, are in `patches/agent/LOG.jsonl`.

### Second scenario: real openFDA lot-code recall notices (`scenarios/fda_lots/`)

40 real FDA food enforcement notices, simulated shelf lots. The hard part is pulling only the affected lots.
Expansion v1's lot code, run as written, pulls 539 good lots: our frozen contract's `Facing` carries no lot, and v1
never hands the shelf lots to its own matcher. Given the lots, it finds 20% of the recalled ones. See
`scenarios/fda_lots/README.md`.

## Gate G5 (numbers frozen, 14:32)

All numbers above were checked against `reports/` and `runs/` (18 checks, 0 mismatches) and are frozen at git tag
`g5-freeze`. Decision on the second scenario: per BUILD.md, the expansion may run it live only if it passes the drill
verifier's hard checks. v2 (+ agent patches) does not (175 hard errors). v1 (+ agent patches) does (0), but its lot
code pulls 539 non-recalled lots as written and finds 20% of recalled lots when given the shelf lots. So the openFDA
lot scenario is not run live; it is reported above as a failure case.

## Demo

```bash
./demo.sh        # runs the core live on 20 stores, verifies it, opens the map (3.6 s; press Space, 20 s replay)
python3 -m http.server -d . 8000   # viewer at /viewer/, live build status at /viewer/status.html
# /viewer/compare.html: who is booked twice? v2 (7,161 double-bookings, 14,117 tasks outside the shift) vs v2 + agent fixes (0)
```

## Reproduce

```bash
python3.11 -m venv .venv && .venv/bin/pip install "google-genai>=2.30.1" pytest pydantic duckdb
# put GEMINI_API_KEY in .env (gitignored)
set -a && source .env && set +a
python tools/build_prompt.py prompts/core_body.md prompts/core.md
python tools/argon_run.py core prompts/core.md 90000
python tools/split_stream.py runs/core/stream.txt --log runs/core/stream_log.jsonl --out gen/core/
PYTHONPATH=gen/core:. python -m recallstorm run --scenario ca_red3 --data data/ --out out/core/
python tools/verify_plan.py out/core/plan.jsonl --labels data/labels.csv --data data/ --report reports/core_plan.json
```
