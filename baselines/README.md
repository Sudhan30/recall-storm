# Baselines C and D (OURS)

Both are written by us, by hand, at the event. They do not use any code from `gen/` (Argon's output).
They implement the same frozen contract (`contract.py`) and are scored by the same tools as Argon's code:
`tools/verify_plan.py` (plan drill) and `acceptance/` (hidden tests). Neither reads `data/labels.csv`.

| | What it is |
|---|---|
| **D** `baselines/d/recallstorm/` | Code only, no LLM. What a competent engineer writes by hand in ~30 minutes: regex alias matcher for Red No. 3 (FD&C/F.D.&C./Rojo, No./#, compact RED3, E127/E-127, erythrosine/eritrosina, OCR o/0 and i/1/l swaps), decoy guards (Red 30/33/40, "red 3-bean", erythorbate), HOLD_VERIFY for generic-color-only or unreadable labels, KEEP when out of scope or before the effective instant. Greedy allocation in store_id order, first-fit-by-case truck packing that splits a store across trucks, round-robin labor inside shifts (floaters only if a store runs out), keyword-classified store-note exceptions, events.jsonl. |
| **C** `baselines/c/recallstorm/` | RAG + LLM + code. A copy of D plus `classifier.py`: for the SKUs D's rules mark HOLD_VERIFY, BM25 retrieval over the rule clauses (`rules.jsonl` source_text sentences + clause_ref) and one `gemini-4-argon` call (google-genai, `thinking_level="low"`, JSON answer: verdict, confidence, match_text, rationale). Any error, unparseable answer or confidence < 0.7 -> HOLD_VERIFY. Answers cached in `runs/baseline_c_cache/` (gitignored) keyed by prompt hash; capped at 300 live calls. |

## Run

```bash
# D
PYTHONPATH=baselines/d:. .venv/bin/python -m recallstorm run --scenario ca_red3 --data data/ --out out/baseline_d/
# C (needs GEMINI_API_KEY unless every answer is cached; writes out/baseline_c/llm_usage.json)
set -a && source .env && set +a
PYTHONPATH=baselines/c:. .venv/bin/python -m recallstorm run --scenario ca_red3 --data data/ --out out/baseline_c/
# score
.venv/bin/python tools/verify_plan.py out/baseline_<x>/plan.jsonl --labels data/labels.csv --data data/ --report reports/baseline_<x>_plan.json
PYTHONPATH=baselines/<x>:. .venv/bin/python -m pytest acceptance -q --junitxml reports/accept_baseline_<x>.xml
```

## Results (ca_red3, 20 stores, 1,212 SKUs; Oct 25 2026)

| | D (code only) | C (RAG + LLM + code) |
|---|---|---|
| verify_plan hard errors | **0** (all checks) | **0** (all checks) |
| PULL precision / recall | 0.9979 / 1.0 (tp 467, fp 1, fn 0) | 0.9979 / 1.0 (same) |
| Decoys pulled | 0 / 483 | 0 / 483 |
| truth KEEP -> | KEEP 688, HOLD 35 | KEEP 723 |
| truth HOLD_VERIFY -> | HOLD 21, PULL 1 | HOLD 15, KEEP 6, PULL 1 |
| PULL facings tasked | 6718 / 6718 | 6718 / 6718 |
| acceptance test_rules | 1218 pass / 36 fail | 1218 / 36 (tests call evaluate_sku without a classifier, so C = D here) |
| acceptance test_allocate | 9 / 9 | 9 / 9 |
| acceptance test_route | 7 / 7 | 7 / 7 |
| plan runtime | 0.3 s | 37 s first run (56 live calls, 8 threads); 0.4 s cached |

All 36 rules failures are `test_labeled_sku_at_deadline` cases (35 truth-KEEP SKUs D holds because of a
generic "artificial color"/"color added", 1 truth-HOLD SKU D pulls). Recall/precision >= 0.90, every alias,
decoy, date, scope, classifier-hook and determinism test passes.

**C's LLM usage:** 56 calls (one per D HOLD_VERIFY SKU), 0 errors; 15 stayed HOLD_VERIFY (model said HOLD or confidence < 0.7,
not counted separately); 44,085 input + 4,218 output tokens (thinking reported as 0 by usage_metadata);
est. **$0.13** at $2/1M in, $10/1M out. The LLM changed **41** verdicts vs D, all HOLD_VERIFY -> KEEP:
35 correct (truth KEEP), 6 wrong (truth HOLD_VERIFY). It never added or removed a PULL.
