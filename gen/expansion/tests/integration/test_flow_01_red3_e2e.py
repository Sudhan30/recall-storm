"""Integration test 01: End-to-end Red No. 3 California recall scenario across 6 packages."""
from datetime import datetime
from contract import PLAN_TYPES, Verdict, load_datapack
from recallstorm.allocate import allocate_substitutes, never_exceeds_stock
from recallstorm.aliases import find_first_match
from recallstorm.core import make_run_id, validate_record
from recallstorm.plan import assemble_plan, validate_plan_refs
from recallstorm.route import manifest_to_record, pack_returns
from recallstorm.rules import evaluate_sku


def test_flow_01_red3_california_e2e():
    pack = load_datapack("data")
    rid = make_run_id("ca_red3", pack.as_of)
    assert rid.startswith("RUN-ca_red3-")

    # 1. Verify alias detection on real FDC SKU
    sprinkles = next(s for s in pack.skus if s.sku_id == "FDC1034191")
    m = find_first_match(sprinkles.ingredients, "RED3")
    assert m is not None and sprinkles.ingredients[m.start:m.end] == "FD&C RED #3"

    # 2. Verify evaluate_sku contract API
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    dec = evaluate_sku(sprinkles, pack.rules, "CA", dl)
    assert dec.verdict == Verdict.PULL
    assert dec.match_text == "FD&C RED #3"

    # 3. Assemble full plan with route manifest packing
    trucks_by_id = {t.truck_id: t for t in pack.trucks}

    def _packer(pulled_cases, skus, trucks, stores):
        mnfs = pack_returns(pulled_cases, skus, trucks, stores)
        return mnfs, [manifest_to_record(mnf, trucks_by_id[mnf.truck_id]) for mnf in mnfs]

    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    records = assemble_plan(pack, scen, manifest_packer=_packer)
    assert validate_plan_refs(records) == []

    # 4. Verify all 9 PLAN_TYPES are present and valid
    present_types = {r["type"] for r in records}
    assert present_types == set(PLAN_TYPES.keys())
    for r in records:
        assert validate_record(r) == []

    # 5. Verify allocate_substitutes conservation directly
    allocs = allocate_substitutes({("WM1563", pack.dc_stock[0].sku_id): 2}, pack.dc_stock, pack.stores)
    assert never_exceeds_stock(pack.dc_stock, allocs) is True
