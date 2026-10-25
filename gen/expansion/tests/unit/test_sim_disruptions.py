"""Unit tests for recallstorm.sim.disruptions."""
from contract import load_datapack
from recallstorm.ingest.manifest_io import sample_datapack
from recallstorm.sim.disruptions import (
    Disruption,
    DisruptionSet,
    absent_associate,
    disruption_report,
    inject_disruption,
    replan_after_disruption,
    seed_disruptions,
    stockout_event,
    truck_delay,
)


def test_disruptions_and_replan():
    pack = sample_datapack(load_datapack("data"), max_stores=2, seed=42)
    d_abs = absent_associate(pack.associates[0].associate_id)
    d_trk = truck_delay(pack.trucks[0].truck_id, 30)
    d_stk = stockout_event(pack.dc_stock[0].dc_id, pack.dc_stock[0].sku_id)

    assert isinstance(d_abs, Disruption)
    ds = DisruptionSet((d_abs, d_trk, d_stk))
    assert len(ds.items) == 3

    p2 = inject_disruption(pack, d_stk)
    assert p2.dc_stock[0].cases == 0

    seeded = seed_disruptions(pack, 99)
    assert len(seeded) == 3
    assert disruption_report(seeded)["total"] == 3

    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    replanned = replan_after_disruption(pack, scen, d_stk)
    assert len(replanned) > 0
