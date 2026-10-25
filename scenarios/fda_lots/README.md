# Scenario 2: `fda_lots` (lot-level recall drill on real openFDA notices)

Real FDA food recall notices land at once. In 20 CA demo stores, pull **only the affected lots** and leave
the other lots of the same item on the shelf. Every window has to end before the deadline.

BUILD.md section 14 says to run this scenario in the demo "only if G5 passed". G5 has **not** passed for
expansion v1: `reports/expansion_plan.json` shows 8,441 hard errors on ca_red3. Treat the v1 numbers
below as part of the experiment, not as a working system.

## What is real and what is simulated

| | Source | Real or simulated |
|---|---|---|
| `data/recalls_fda.jsonl` (40 notices) | openFDA Food Enforcement API, `report_date:[20240101 TO 20261025]`, status Ongoing or Completed. Raw pages are cached in `data/raw/openfda/` (gitignored). | **Real** notice fields (recall_number, firm, product_description, reason, class, report_date, distribution_pattern, code_info). The parsed columns are **ours** (lots, lot_ranges, date_windows, scope, parse_confidence). `sim_sku_id`/`sim_gtin` are a **simulated** item-master cross-reference. |
| `data/skus_fda.jsonl` (40) | Built from the notice text: name, brand = recalling firm, category by keyword | **Simulated**. GTINs use the GS1 restricted-circulation prefix 02. Real UPCs from a notice are kept only as `_upc_real`. |
| `data/lots.jsonl` (1,002 shelf lots) | Seed 418 | **Simulated**. Covers which stores carry which item, the loc of each lot, the lot strings, best-by dates and units. |
| `data/labels_fda.csv` | Deterministic, from the parsed terms (rule below) | **Ours** |
| `data/scenario_fda_lots.json` | as_of 2026-12-29 08:00 PT, deadline 2026-12-31 08:00 PT (48 h) | **Ours**. The labor window is the existing overnight shift in `associates.jsonl`. |

openFDA data is public domain (CC0, https://open.fda.gov/license/), under https://open.fda.gov/terms/.
openFDA says: "assume all results are unvalidated."

This is a **drill replay**. Notices from 2024 to 2026 are treated as if they all arrived on 2026-12-29.
Some best-by dates on the simulated shelves are therefore already past.

## Data build and ground truth (`data/build_fda_lots.py`)

- **Selection.** Of 4,075 notices fetched, 905 are Ongoing or Completed. Our parser rates 462 of those
  high or medium confidence, a **parse rate of 51%**. One notice is chosen per openFDA event, with seed 418:
  - 34 notices distributed to CA (pattern names CA or California, or is nationwide or US-wide).
    This includes 6 deliberately ambiguous ones.
  - 6 notices distributed only to other states. These have a catalog SKU but no shelf stock.
  - By kind, over all 40: 19 lot lists, 1 lot range (Batch X through Y), 11 date lists, 8 date windows, 1 "all lot codes".
- **Shelf edge cases.**
  - Recalled lots sit next to near-miss lots of the same SKU: the next or previous number, one lot just outside a range, a best-by date 1 day outside a window.
  - Lot strings are written in different ways: lower case, a dash inserted, punctuation dropped, a `LOT ` prefix (167 shelf lots).
  - Month-only expiry dates (for example `EXP 03/2027`).
  - A "Best By Date **before** 01/15/2027" notice, where the window is exclusive.
  - "up to and including" and "on or before" windows that are open at the start.
- **Truth per shelf lot** (`norm` = upper case, drop a leading LOT/BATCH word, drop non-alphanumerics):
  1. Low parse confidence gives **HOLD_VERIFY**. This covers multi-product numbered lists, DD/MM dates, lot-format descriptions, purchase or production dates, and lot-like tokens we could not attribute.
  2. "All lots" gives **PULL**.
  3. If the notice lists lots, it is PULL when `norm(lot)` is listed or falls inside a listed range (same length, string compare). Otherwise KEEP. The lots decide; dates are not used.
  4. If the notice lists only dates, it is PULL when best_by falls inside a window. Otherwise KEEP.
- **Label counts:** 276 PULL, 539 KEEP, 187 HOLD_VERIFY. The bases are lot_exact 100, lot_range 10,
  date_window 137, all_lots 29, not_listed 539 and ambiguous 187.
- **Caveat.** The labels follow *our* parse of code_info. We checked the 40 parses by reading the
  notices, but this was a spot check, not an independent second annotator.

## Verifier (`tools/verify_lots.py`)

- **Mapping a task to a lot.** The verifier uses the task's optional `lot` field (normalized). If there is
  none, it uses the task's `loc`, because each simulated lot has its own position and the contract
  `Facing` has no lot field.
- **Hard checks:**
  - schema
  - reference: unknown store, SKU, associate or evidence_id, or a task that maps to no shelf lot
  - **overpull**: a non-recalled lot that was pulled. This must be 0.
  - coverage: every truth-PULL lot has a PULL task
  - deadline
  - labor: window inside the shift, associate belongs to that store, no overlapping windows, total minutes within the shift
- **Soft checks:** HOLD lots left untouched, and PULL quantity below the shelf units.
- **Reused code.** Errs, rows, parse_dt and window are imported from `tools/verify_plan.py`. The labor
  logic is re-implemented, because in verify_plan it is inline in `main()`.

## How to run

```bash
.venv/bin/python data/build_fda_lots.py            # reads the cache; --fetch refreshes it from openFDA
# baseline D-lots (ours, code only)
.venv/bin/python baselines/d_lots/plan_lots.py --scenario fda_lots --data data/ --out out/baseline_d_lots/
# expansion v1 (gen/expansion, unedited) through the adapter: three ways
.venv/bin/python scenarios/fda_lots/adapter.py --mode gs1         # v1's scenario_gs1.recall_plan (as written)
.venv/bin/python scenarios/fda_lots/adapter.py --mode gs1_lotinv  # v1's lot_pull_tasks, fed the shelf lots
.venv/bin/python scenarios/fda_lots/adapter.py --mode cli         # v1's real CLI: python -m recallstorm run --scenario fda_lots
# score
.venv/bin/python tools/verify_lots.py out/<name>/plan.jsonl --name <name>     # -> reports/<name>_lots.json
```

### How v1 was invoked

- **The CLI path does no lot work.** `python -m recallstorm run --scenario fda_lots` accepts the scenario
  id, but `cmd_run` always calls `plan.assemble_plan`, which is the Red No. 3 pipeline. The only lot code
  is `recallstorm.scenario_gs1`, which can only be used as a library:
  - `recall_from_openfda(raw_report)` returns a `Gs1Scenario` for **one** recall.
  - `recall_plan(Gs1Scenario, DataPack)` returns the records.
- **What the adapter does.** It writes a contract DataPack directory with one Facing per shelf lot. It
  loops over the 40 notices and feeds each raw notice to v1, so v1's own parser picks the lots. It
  replaces only the GTINs (our item-master mapping) and the scenario times.
- **No crashes.** No v1 call crashed. The logs are in `reports/expansion_fda_lots*_adapter_log.json` and `reports/expansion_fda_lots_cli_log.txt`.

## Results (Oct 25 2026; 1,002 shelf lots, 276 truth-PULL)

| Plan | Hard errors | Lot PULL precision / recall | Non-recalled lots pulled | HOLD lots → | Notes |
|---|---|---|---|---|---|
| **baseline D-lots** (ours, code only) | **38** (coverage 38) | **1.000 / 0.862** (tp 238, fp 0, fn 38) | **0** | 101 HOLD, 86 untouched | Misses come from its own parser bugs: "Lot: B2025 Expiration" becomes one token, and "2026 AUGUST 31" is misread. 0 labor and 0 deadline errors. |
| v1 `gs1` (recall_plan as written) | 3,545 (labor 2,004, overpull 539, reference 1,002) | 0.275 / 1.000 (tp 276, fp 726) | **539** | 187 PULL | See "Where v1 broke" below. |
| v1 `gs1_lotinv` (v1 lot matcher, adapter passes shelf lots) | 352 (coverage 222, labor 130) | 0.831 / 0.196 (tp 54, fp 11, fn 222) | 0 | 11 PULL, 176 untouched | Date-only recalls fall back to `LOT2026A`, so nothing matches. |
| v1 `cli` (`python -m recallstorm run --scenario fda_lots`) | 276 (coverage 276) | – / 0.000 | 0 | untouched | Exit 0. Red No. 3 verdicts: 40 SKU KEEP, 0 shelf tasks. |

### Where v1 broke

- `recall_plan` never passes lot inventory to `lot_pull_tasks`, so it pulls **every** facing of a matched SKU.
- Its window is hardcoded to `[as_of, 2026-12-31T06:00]` with a single associate `{store}-A00`. That gives windows outside the shift and overlapping windows for one associate.
- It does not pass `recall_id` to `lot_pull_tasks`, so the tasks' evidence_ids point at the default `OPENFDA_F-0100-2026` evidence, which does not exist.
- Its parser turns keywords into lots: "All lot codes" becomes `CODES`, and "LOT NUMBER I24BI-01A" becomes `NUMBER`.
- Notices with only dates get the placeholder lot `LOT2026A`.
- It never filters by distribution: it takes the first state in the pattern as the scenario state.

## Notes for v2 (`recallstorm/recall_lots/`)

The v2 spec adds parsers and matchers: `fda_notice_parser`, `lot_pattern_matcher`, `best_by_window`,
`distribution_list`, `depth_of_recall` and others. Its `scenario_gs1` keeps the same signatures as v1.
Check whether anything wires these into `cli.cmd_run` or `scenario_gs1.recall_plan`. If nothing does,
point the adapter at the new parser/matcher functions, the same way `gs1_lotinv` does.

The inputs v2 should consume:
- raw openFDA dicts: the `RAW_KEYS` in the adapter, read from `recalls_fda.jsonl`
- shelf lots: `lots.jsonl` (store, sku, loc, lot, best_by, units)
- the contract DataPack in `out/fda_lots_v1_data/`

v2's plan tasks have to say which lot they mean, through `loc` or an extra `lot` field.
