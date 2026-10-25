# Recall Storm Architecture

Recall Storm is a deterministic regulatory compliance and retail store execution platform that translates federal and state product bans and recall feeds into store-by-store shelf pull playbooks, DC substitute allocations, return truck manifests, and discrete-event simulations.

## Package Dependency Flow

1. `recallstorm.core`: Deterministic SHA-based IDs (`RUN`, `TSK`, `EVD`, `ALC`, `MNF`, `HND`, `EXC`), exception hierarchy, configuration, structured JSONL logging with PII redaction, timezone-aware wall-clock arithmetic, and `PLAN_TYPES` record validation.
2. `recallstorm.ingest`: Parsers for USDA FoodData Central (FDC), Open Food Facts (OFF), openFDA enforcement reports, CPSC recalls, FSIS/FDA RSS feeds, OCR label payloads, vendor catalogs, store lists, planograms, and staffing rosters.
3. `recallstorm.aliases`: Multilingual additive lexicon (`en`, `es`, `fr`, `de`), accent folding, OCR repair, decoy rejection (`Red 40`, `D&C Red 33`, `3 red bell peppers`), vague/unreadable label detection, and multi-component bundle splitting.
4. `recallstorm.rules`: Regulatory rule engine implementing `evaluate_sku(sku, rules, state, at, classifier=None) -> SkuDecision` across CA AB 418 (Red 3, BVO, potassium bromate, propylparaben), FDA Red No. 3 food/drug revocations, FDA BVO revocation, Minnesota PFAS (`Minn. Stat. 116.943`), and CARB multi-purpose lubricant VOC limits (`17 CCR 94509`).
5. `recallstorm.adjudicate`: Evidence card linking with exact character spans, `HeuristicClassifier` and `GeminiClassifier`, `HOLD_VERIFY` review queues, QA stratified sampling, compliance officer overrides, and audit trails.
6. `recallstorm.gs1`: Modulo-10 GTIN check digits, Application Identifiers (`01`, `10`, `11`, `17`, `21`), GS1 Digital Link URIs, EPCIS events, and lot/expiry range matching.
7. `recallstorm.store`: 2D store layouts, serpentine aisle ordering, Manhattan walking distances, backroom staging, signage, and classification of free-text `StoreNote` records into all six `ExceptionKind` values.
8. `recallstorm.labor`: Associate shift calendars, labor compliance checks, task duration estimates, and district floater dispatching with strict one-store-per-window guarantees.
9. `recallstorm.allocate`: Substitute case demand calculation, proportional/priority allocation (`allocate_substitutes`) with strict DC stock conservation, and `SUB_TRANSFER` handoffs.
10. `recallstorm.plan`: Task builder (`PULL`, `HOLD_VERIFY`, `PLACE_SUB`, `TAG_FLASH`), store playbooks, exception linking, deadline enforcement, and full `plan.jsonl` assembly.
11. `recallstorm.sim`: Discrete-event simulation (`MOVE`, `PULL`, `PLACE`, `DONE`), walking path replay, disruption injection, and completion curves.
12. `recallstorm.scenario_gs1`: Lot-specific recall scenarios driven by openFDA enforcement reports.
13. `recallstorm.route`: Return load aggregation, stop ordering, and First-Fit Decreasing truck bin-packing (`pack_returns`).
14. `recallstorm.report`: Drill summaries, 6-category invariant checks, store/DC packet exports, and HTML/JSON dashboards.
15. `recallstorm.cli`: Command-line interface (`python -m recallstorm run --scenario <id> --data <dir> --out <dir>`).
