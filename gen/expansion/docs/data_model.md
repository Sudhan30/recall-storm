# Recall Storm Data Model & Schemas

All shared domain entities and enumerations are defined in `contract.py` at the repository root and used unchanged across every package.

## Input Entities (`DataPack`)

- `Sku`: `sku_id`, `gtin` (14-digit), `name`, `brand`, `category`, `ingredients`, `is_food`, `is_ingested_drug`, `case_units`, `case_cube_ft3`, `case_weight_lb`.
- `Store`: `store_id`, `format` (`SUPERCENTER | DISCOUNT | NEIGHBORHOOD | SAMS`), `state`, `city`, `lat`, `lon`, `district`, `dc_id`, `tz`.
- `Facing`: `store_id`, `sku_id`, `loc` (`Location(aisle, bay, shelf, pos)`), `units`.
- `Associate`: `associate_id`, `store_id` (`None` for floaters), `district`, `is_floater`, `shift_start`, `shift_end` (tz-aware).
- `Truck`: `truck_id`, `dc_id`, `cube_ft3`, `weight_lb`, `depart`.
- `DcStock`: `dc_id`, `sku_id`, `cases`.
- `StoreNote`: `note_id`, `store_id`, `text`.
- `Rule`: `rule_id`, `additive`, `aliases`, `jurisdictions`, `applies_to`, `effective` (naive local wall-clock), `clause_ref`, `source_text`.

## Output `plan.jsonl` Record Types (`PLAN_TYPES`)

Every record in `plan.jsonl` includes `"type"` and `"src"` (the repo-relative path of the emitting module):

1. `run`: `run_id`, `scenario_id`, `generator`, `as_of`, `rule_ids`, `src`
2. `sku_verdict`: `sku_id`, `gtin`, `verdict` (`PULL | HOLD_VERIFY | KEEP`), `additive`, `match`, `rule_ids`, `jurisdictions`, `decided_by` (`RULE | MODEL`), `evidence_id`, `src`
3. `evidence`: `evidence_id`, `sku_id`, `rule_id`, `clause_ref`, `source_span` (`[start, end]`), `rationale`, `src`
4. `store_playbook`: `store_id`, `format`, `deadline`, `windows`, `counts`, `associate_ids`, `exception_ids`, `manifest_ids`, `src`
5. `shelf_task`: `task_id`, `store_id`, `sku_id`, `action` (`PULL | HOLD_VERIFY | PLACE_SUB | TAG_FLASH`), `loc`, `qty_units`, `associate_id`, `window`, `seq`, `evidence_id`, `sub_sku_id`, `alloc_id`, `src`
6. `exception`: `exc_id`, `store_id`, `kind` (`DSD_VENDOR_PULL | ENDCAP_DISPLAY | TOPSTOCK | PICKUP_TOTES | NOT_ON_PLANOGRAM | UNCLEAR_LABEL`), `note_id`, `resolution`, `task_ids`, `src`
7. `allocation`: `alloc_id`, `dc_id`, `sub_sku_id`, `store_id`, `qty_cases`, `dc_balance_after`, `src`
8. `handoff`: `handoff_id`, `kind` (`FLOATER | SUB_TRANSFER | RETURN_CONSOLIDATION`), `from_id`, `to_id`, `window`, `qty`, `ref_ids`, `src`
9. `route_manifest`: `manifest_id`, `truck_id`, `dc_id`, `stops`, `limits`, `depart`, `src`

## Output `events.jsonl` Schema

Each line in `events.jsonl` represents a discrete simulation event:
```json
{"t": "2026-12-30T22:01:15-08:00", "store_id": "WM1563", "associate_id": "WM1563-A04", "kind": "PULL", "loc": {"aisle": "A01", "bay": 1, "shelf": 4, "pos": 3}, "task_id": "TSK-WM1563-..."}
