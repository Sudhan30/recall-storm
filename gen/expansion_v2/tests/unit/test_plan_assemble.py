"""Unit tests for recallstorm.plan.assemble."""
from datetime import datetime
from contract import Associate, DataPack, DcStock, Facing, Location, Sku, Store, StoreFormat, StoreNote
from recallstorm.plan.assemble import (
    PlanAssembler,
    assemble_plan,
    merge_plans,
    plan_hash,
    plan_records,
    plan_stats,
    plan_to_jsonl,
    run_record,
    validate_plan_refs,
)
from recallstorm.rules.red3 import red3_rules


def _sample_pack() -> DataPack:
    s1 = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, FD&C RED #3.", True, False, 6, 2.0, 10.0)
    s2 = Sku("VAR0172", "00012345678905", "Sub Sprinkles", "B", "baking", "SUGAR, BEET JUICE.", True, False, 6, 2.0, 10.0)
    st = Store("WM1563", StoreFormat.SUPERCENTER, "CA", "Lancaster", 34.6, -118.1, "D06", "DC_CENTRAL", "America/Los_Angeles")
    f = Facing("WM1563", "FDC1034191", Location("A01", 1, 1, 1), 12)
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    assoc = Associate("WM1563-A04", "WM1563", "D06", False, t0, t1)
    stock = [DcStock("DC_CENTRAL", "VAR0172", 5)]
    note = StoreNote("N0012", "WM1563", "Topstock overflow above aisle 1.")
    return DataPack([s1, s2], [st], [f], [assoc], [], stock, {"FDC1034191": ["VAR0172"]}, [note], red3_rules(), t0)


def test_assemble_plan(tmp_path):
    pack = _sample_pack()
    scenario = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, scenario)
    assert validate_plan_refs(recs) == []
    stats = plan_stats(recs)
    assert stats["run"] == 1
    assert stats["sku_verdict"] == 2
    assert stats["evidence"] == 1
    assert stats["allocation"] == 1
    assert stats["shelf_task"] == 3
    assert stats["exception"] == 1
    assert stats["store_playbook"] == 1

    out_file = tmp_path / "plan.jsonl"
    assert plan_to_jsonl(recs, str(out_file)) == len(recs)
    assert plan_hash(recs) == plan_hash(recs)
    assert len(merge_plans(recs, recs)) == len(recs)
    assert run_record("ca_red3", "2026-12-30T18:00:00-08:00", ["CA_AB418_RED3"])["type"] == "run"
    assert len(plan_records(recs[0], [], [], [], [], [], [], [], [])) == 1
    assert PlanAssembler(pack, scenario).scenario["state"] == "CA"
