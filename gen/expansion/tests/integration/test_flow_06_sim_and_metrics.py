"""Integration test 06: Plan assembly -> Simulation replay -> Walking -> Metrics -> Report dashboard."""
from contract import load_datapack
from recallstorm.core import stable_dumps
from recallstorm.ingest import sample_datapack
from recallstorm.plan import assemble_plan
from recallstorm.report import dashboard_data, dashboard_html
from recallstorm.sim import (
    completion_curve,
    detect_late_events,
    simulate_plan,
    store_completion,
    walking_summary,
)
from recallstorm.store import locate_sku


def test_flow_06_sim_and_dashboard():
    pack = sample_datapack(load_datapack("data"), max_stores=3, seed=42)
    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    records = assemble_plan(pack, scen)
    events = simulate_plan(records)
    assert len(events) > 0
    assert detect_late_events(events, scen["deadline"]) == []
    curve = completion_curve(events)
    assert curve[-1][1] == sum(1 for r in records if r["type"] == "shelf_task")

    st_id = pack.stores[0].store_id
    assert store_completion(events, st_id) == 1.0
    locs = locate_sku(pack.facings, st_id, pack.facings[0].sku_id)
    assert walking_summary(locs)["stop_count"] == len(locs)

    dash = dashboard_data(records, events, pack.stores)
    assert len(stable_dumps(dash)) > 20
    assert "Recall Storm" in dashboard_html(dash)
