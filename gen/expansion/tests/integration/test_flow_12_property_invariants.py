"""Integration test 12: Property & invariant tests across randomized seeds and demand distributions."""
from datetime import datetime
from contract import load_datapack
from recallstorm.allocate import allocate_substitutes, never_exceeds_stock
from recallstorm.core import is_before_deadline
from recallstorm.ingest import sample_datapack
from recallstorm.plan import assemble_plan, plan_hash
from recallstorm.report import run_all_checks
from recallstorm.route import manifest_to_record, overload_report, pack_returns, validate_returns
from recallstorm.rules import evaluate_sku


def test_flow_12_property_invariants():
    full_pack = load_datapack("data")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")

    # Property 1: Determinism across repeated runs
    sub_pack = sample_datapack(full_pack, max_stores=6, seed=101)
    trucks_by_id = {t.truck_id: t for t in sub_pack.trucks}

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
    p1 = assemble_plan(sub_pack, scen, manifest_packer=_packer)
    p2 = assemble_plan(sub_pack, scen, manifest_packer=_packer)
    assert plan_hash(p1) == plan_hash(p2)
    assert run_all_checks(p1, sub_pack, scen["deadline"]).passed is True

    # Property 2: Every PULL decision has an exact substring span into sku.ingredients
    for sku in full_pack.skus:
        dec = evaluate_sku(sku, full_pack.rules, "CA", dl)
        if dec.verdict.value == "PULL":
            assert dec.match_start is not None and dec.match_end is not None
            assert sku.ingredients[dec.match_start:dec.match_end] == dec.match_text

    # Property 3: Stock conservation holds under extreme demand (>100x stock)
    extreme_demand = {
        (st.store_id, d.sku_id): 50
        for st in sub_pack.stores
        for d in sub_pack.dc_stock[:4]
    }
    allocs = allocate_substitutes(extreme_demand, sub_pack.dc_stock, sub_pack.stores)
    assert never_exceeds_stock(sub_pack.dc_stock, allocs) is True

    # Property 4: Route packing conserves cases and respects truck limits across varying loads
    synthetic_pulls = {(st.store_id, full_pack.skus[0].sku_id): (idx + 1) * 3 for idx, st in enumerate(sub_pack.stores)}
    manifests = pack_returns(synthetic_pulls, full_pack.skus, sub_pack.trucks, sub_pack.stores)
    assert overload_report(manifests, trucks_by_id) == []
    assert validate_returns(synthetic_pulls, manifests) == []

    # Property 5: Every window in plan ends strictly before scenario deadline
    for r in p1:
        if "window" in r:
            assert is_before_deadline(r["window"][1], dl) is True
