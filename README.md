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
