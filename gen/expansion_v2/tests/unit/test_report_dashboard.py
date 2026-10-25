"""Unit tests for recallstorm.report.dashboard."""
from recallstorm.plan.assemble import assemble_plan
from recallstorm.report.dashboard import (
    DashboardBuilder,
    DashboardModel,
    dashboard_data,
    dashboard_html,
    dashboard_to_json,
    kpi_tiles,
    map_points,
    store_status_colors,
    timeline_series,
)
from recallstorm.sim.replay import simulate_plan
from tests.unit.test_plan_assemble import _sample_pack


def test_report_dashboard():
    pack = _sample_pack()
    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, sc)
    evs = simulate_plan(recs)
    pbs = [r for r in recs if r.get("type") == "store_playbook"]

    assert store_status_colors(pbs)["WM1563"] == "RED"
    assert len(map_points(pack.stores, pbs)) == 1
    assert len(timeline_series(evs)) == 3
    assert len(kpi_tiles(recs)) == 4
    model = dashboard_data(recs, evs, pack.stores)
    assert isinstance(model, DashboardModel)
    assert "Pulled SKUs" in dashboard_to_json(model)
    assert "<html>" in dashboard_html(model)
    assert len(DashboardBuilder(recs).records) == len(recs)
