# Recall Storm Operations Runbook

## Running a Recall Scenario

To execute a full recall scenario and emit `plan.jsonl` and `events.jsonl`:

```bash
python -m recallstorm run --scenario ca_red3 --data data/ --out out/ca_red3/
```

## Validating Data & Plan Invariants

To validate the input `DataPack` and verify all referential, stock conservation, truck capacity, labor, and deadline invariants on an emitted `plan.jsonl`:

```bash
python -m recallstorm validate --data data/ --plan out/ca_red3/plan.jsonl
```

## Inspecting Plan Statistics & Narrative

```bash
python -m recallstorm stats --plan out/ca_red3/plan.jsonl
python -m recallstorm explain --plan out/ca_red3/plan.jsonl
```

## Replaying Simulation Events

```bash
python -m recallstorm replay --plan out/ca_red3/plan.jsonl --out out/ca_red3/events.jsonl
```

## Running the Test Suite

```bash
pytest -q
