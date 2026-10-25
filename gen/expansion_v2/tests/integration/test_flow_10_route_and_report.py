"""Integration test 10: core -> rules -> allocate -> route -> report."""
from datetime import datetime
from contract import Truck
from recallstorm.plan.assemble import assemble_plan
from recallstorm.report.checks import run_all_checks
from recallstorm.report.summary import drill_summary
from recallstorm.route import pack_returns
from recallstorm.route.packing import manifest_to_record
from recallstorm.route.returns import returned_cases
from recallstorm.rules import evaluate_sku
from tests.unit.test_plan_assemble import _sample_pack


def test_flow_route_and_report():
    pack = _sample_pack()
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    t0 = Truck("DC_CENTRAL-T0", "DC_CENTRAL", 3400.0, 40000.0, dep)
    pack.trucks.append(t0)

    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    decs = {s.sku_id: evaluate_sku(s, pack.rules, "CA", dl) for s in pack.skus}
    pulled = returned_cases(pack.facings, decs, {s.sku_id: s for s in pack.skus})
    mnfs = pack_returns(pulled, pack.skus, pack.trucks, pack.stores)
    assert len(mnfs) == 1
    mnf_recs = [manifest_to_record(m, t0) for m in mnfs]

    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, sc, manifests=mnf_recs)
    rep = run_all_checks(recs, pack, sc["deadline"])
    assert rep.passed is True
    assert drill_summary(recs)["manifests"] == 1
