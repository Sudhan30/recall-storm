# Recall Storm Operations Runbook

## CLI Execution
Run a full recall scenario and generate `plan.jsonl` and `events.jsonl`:
```bash
python -m recallstorm run --scenario ca_red3 --data data/ --out out/ca_red3/
```

Other supported subcommands:
- `python -m recallstorm validate --data data/`
- `python -m recallstorm stats --data data/`
- `python -m recallstorm explain --plan out/ca_red3/plan.jsonl --sku FDC1034191`
- `python -m recallstorm replay --plan out/ca_red3/plan.jsonl --out out/ca_red3/events.jsonl`
- `python -m recallstorm scenarios --data data/`

## Operational Invariants
1. **Deadline Compliance**: Every task, handoff, and store playbook window ends strictly before the scenario deadline.
2. **Stock Conservation**: Substitute allocations per `(dc_id, sub_sku_id)` never exceed `DcStock.cases`, use integer cases, and tie-break deterministically by `store_id`.
3. **Truck Capacity & Return Conservation**: Every pulled non-DSD case is packed onto a `RouteManifest` stop without exceeding `Truck.cube_ft3` or `Truck.weight_lb`.
4. **Referential Integrity**: Every `evidence_id`, `alloc_id`, `task_id`, `exc_id`, and `manifest_id` referenced in `plan.jsonl` resolves to an emitted record in the same file.
