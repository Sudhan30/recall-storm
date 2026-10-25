# Recall Storm Data Model

All core entities and vocabulary enums are imported unchanged from `contract.py`:

- **Enums**:
  - `Verdict`: `PULL`, `HOLD_VERIFY`, `KEEP`
  - `Action`: `PULL`, `HOLD_VERIFY`, `PLACE_SUB`, `TAG_FLASH`
  - `StoreFormat`: `SUPERCENTER`, `DISCOUNT`, `NEIGHBORHOOD`, `SAMS`
  - `ExceptionKind`: `DSD_VENDOR_PULL`, `ENDCAP_DISPLAY`, `TOPSTOCK`, `PICKUP_TOTES`, `NOT_ON_PLANOGRAM`, `UNCLEAR_LABEL`
  - `HandoffKind`: `FLOATER`, `SUB_TRANSFER`, `RETURN_CONSOLIDATION`
  - `DecidedBy`: `RULE`, `MODEL`
- **Input Dataclasses**: `Sku`, `Store`, `Location`, `Facing`, `Associate`, `Truck`, `DcStock`, `StoreNote`, `Rule`, `DataPack`.
- **Output Dataclasses**: `SkuDecision`, `Allocation`, `Stop`, `RouteManifest`.
- **JSONL Outputs**:
  - `plan.jsonl`: Every record includes `"type"` (one of the 9 keys in `PLAN_TYPES`), all required fields for that type, and `"src"` (the repo-relative path of the emitting module).
  - `events.jsonl`: Ordered discrete simulation events with `"t"`, `"store_id"`, `"associate_id"`, `"kind"` (`MOVE`|`PULL`|`PLACE`|`DONE`), `"loc"`, and `"task_id"`.
