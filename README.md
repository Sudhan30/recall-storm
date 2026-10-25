# Recall Storm

Gemini 4 Argon SF Hackathon, Track 1 (Million Token Engineering), Oct 25, 2026.

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
| Expansion v2 (`gen/expansion_v2`) | _pending_ | | | | | |

Continuation was proven before the big runs: a 2-hop probe (`runs/probe/`, 32K-token seam) passed `tools/seam_check.py`.

### The drill (`tools/verify_plan.py`: missed shelves, double-booked associates, late tasks, stock, truck capacity, look-alikes pulled)

| Build | Plan mistakes (hard errors) | Red No. 3 products found | Look-alikes pulled | Hidden tests passed |
|---|---|---|---|---|
| Core, Argon's first draft (unedited) | 350 | 442 / 467 | 0 / 483 | 1,152 / 1,263 |
| Core + 3 small hand fixes (`patches/core/`) | **0** | **467 / 467** | 0 / 483 | 1,258 / 1,263 |
| Expansion v1, unedited | 8,441 | 411 / 467 | 3 / 483 | 1,194 / 1,270 |
| Expansion v1 + 3 managed-agent patches (`patches/agent/`) | **0** | **467 / 467** | 0 / 483 | 1,262 / 1,270 |
| Baseline D: code only, written by us | 0 | 467 / 467 | 0 / 483 | 1,234 / 1,270 |
| Baseline C: retrieval + LLM + our code | 0 | 467 / 467 | 0 / 483 | 1,234 / 1,270 |

The core has no `route/` package, so its hidden route tests are skipped (1,263 instead of 1,270).

### Matched packages: written inside one long generation vs fresh short calls (same hidden tests)

| Package | Core (in-stream) | Expansion v1 (in-stream) | Baseline B (fresh short call) |
|---|---|---|---|
| rules | 1,143 / 1,254 | 1,179 / 1,254 | 1,240 / 1,254 |
| allocate | 9 / 9 | 9 / 9 | 9 / 9 |
| route | — | 6 / 7 | 7 / 7 |

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

All attempts, including the failed ones, are in `patches/agent/LOG.jsonl`.

### Second scenario: real openFDA lot-code recall notices (`scenarios/fda_lots/`)

40 real FDA food enforcement notices, simulated shelf lots. The hard part is pulling only the affected lots.
Expansion v1's lot code, run as written, pulls 539 good lots: our frozen contract's `Facing` carries no lot, and v1
never hands the shelf lots to its own matcher. Given the lots, it finds 20% of the recalled ones. See
`scenarios/fda_lots/README.md`.

## Demo

```bash
./demo.sh        # runs the core live on 20 stores, verifies it, opens the map (3.6 s; press Space, 20 s replay)
python3 -m http.server -d . 8000   # viewer at /viewer/, live build status at /viewer/status.html
# /viewer/compare.html: who is booked twice? v1 as written (7,631 double-bookings) vs v1 + agent fixes (0)
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
