"""Unit tests for recallstorm.report.dashboard."""
from contract import Store, StoreFormat
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


def test_dashboard_generation():
    db = DashboardBuilder()
    assert "Recall Storm" in db.title
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    recs = [
        {"type": "sku_verdict", "verdict": "PULL"},
        {"type": "store_playbook", "store_id": "WM1", "counts": {"total_tasks": 2}, "exception_ids": ["EXC-1"]},
    ]
    evs = [{"kind": "DONE", "t": "2026-12-30T22:05:00-08:00"}]

    assert store_status_colors([recs[1]]) == {"WM1": "amber"}
    pts = map_points([st], [recs[1]])
    assert len(pts) == 1 and pts[0]["color"] == "amber"
    assert len(timeline_series(evs)) == 1
    tiles = kpi_tiles(recs, evs)
    assert len(tiles) == 4
    dm = DashboardModel(tuple(tiles), tuple(pts))
    assert len(dm.kpis) == 4

    data = dashboard_data(recs, evs, [st])
    assert "kpis" in dashboard_to_json(data)
    assert "<html>" in dashboard_html(data)
