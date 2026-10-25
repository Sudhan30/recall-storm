# Repair log

Patches apply on top of unedited Argon output. They are never counted in Argon's token totals, and every
score is reported twice: pre-repair (`gen/core`) and post-repair (`gen/core_patched`, built by
`patches/apply_core.sh`).

## core/001_aliases_spaced_fdc_and_eritrosina.patch

- **Author:** us, by hand (not the Argon repair loop). 5 regex edits in `recallstorm/aliases/detector.py`.
- **Failure:** two PULL SKUs kept as KEEP.
  - `F D & C Red No. 3` (spaced): the FD&C pattern required `fd` written together, and the D&C decoy
    pattern `(?<!f)d\s*&\s*c` matched `D & C Red No. 3` and vetoed the match.
  - `eritrosina` (Spanish/Italian): the erythrosine pattern required an `h` and an `-e`/no ending.
- **Fix:** allow `F D & C` / `F.D.&C.` spacing and dots; lookbehinds `(?<!f )` `(?<!f\.)` on the D&C decoy;
  optional `h`, `é`, and `-a` ending on erythrosine.
- **Not fixed on purpose:** "Red 3 Ranch seasoning blend (paprika)", a decoy we planted. A fix would just
  encode our test.
- **Result** on the placeholder pack (186 SKUs, seed 418): precision 0.912 → 0.925, recall 0.838 → 1.000.
  Argon's own unit tests: 42 passed, 1 skipped, before and after.

## core/002_aliases_ocr_n0_and_rojo.patch

- **Author:** us, by hand. 2 regex edits in `recallstorm/aliases/detector.py`, on top of 001.
- **Failure on the real pack** (1,212 SKUs): 8 PULL SKUs with `RED N0. 3` (zero for O, OCR noise) and
  5 with `FD&C Rojo No. 3` (Spanish), kept or held.
- **Fix:** accept `N0`/`Nº` for "No", and `rojo`/`rouge`/`rosso` for "red", only before the number 3.
  `RED N0. 30`, `FD&C Rojo No. 40` and `D&C Red No. 33` still do not match.
- **Not fixed (rules logic, not aliases):** 78 KEEP SKUs go to HOLD_VERIFY because any "ARTIFICIAL COLORS"
  triggers a hold, even when the label then names the dyes ("ARTIFICIAL COLORS (RED 40, YELLOW 6)").

## Scores on the real pack (data commit 5bf1814)

| Build | PULL precision | PULL recall | KEEP pulled | KEEP held |
|---|---|---|---|---|
| `gen/core` (Argon, unedited) | 0.998 | 0.946 | 0 | 78 |
| `gen/core_patched` (001 + 002) | 0.998 | 1.000 | 0 | 78 |

The single non-PULL item pulled is labeled HOLD_VERIFY (a label stating the US version uses Red 40 in place of
erythrosin). Argon's own unit tests: 42 passed, 1 skipped, before and after.
