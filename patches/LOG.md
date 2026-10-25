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
