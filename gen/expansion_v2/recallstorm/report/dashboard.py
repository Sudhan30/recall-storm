"""Dashboard data models, map points, KPI tiles, and HTML rendering."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json

from contract import Store
from recallstorm.report.summary import drill_summary
from recallstorm.sim.metrics import completion_curve


@dataclass
class DashboardModel:
    """Data model backing the Recall Storm operational dashboard."""

    kpis: list[dict] = field(default_factory=list)
    points: list[dict] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)


@dataclass
class DashboardBuilder:
    """Builder for DashboardModel."""

    records: list[dict]


def store_status_colors(playbooks: list[dict]) -> dict[str, str]:
    """Assign status color ('RED' if tasks > 0, else 'GREEN') per store_id."""
    out: dict[str, str] = {}
    for p in playbooks:
        st_id = str(p.get("store_id", ""))
        tasks = int(p.get("counts", {}).get("tasks", 0))
        out[st_id] = "RED" if tasks > 0 else "GREEN"
    return out


def map_points(stores: list[Store], playbooks: list[dict]) -> list[dict]:
    """Build geographic map points for stores with status colors and task counts."""
    pb_map = {str(p.get("store_id")): p for p in playbooks}
    colors = store_status_colors(playbooks)
    out: list[dict] = []
    for s in sorted(stores, key=lambda x: x.store_id):
        pb = pb_map.get(s.store_id, {})
        out.append(
            {
                "store_id": s.store_id,
                "city": s.city,
                "lat": s.lat,
                "lon": s.lon,
                "color": colors.get(s.store_id, "GREEN"),
                "tasks": int(pb.get("counts", {}).get("tasks", 0)),
            }
        )
    return out


def timeline_series(events: list[dict]) -> list[dict]:
    """Convert simulation completion curve into [{t, done}] timeline points."""
    return [{"t": t, "done": cnt} for t, cnt in completion_curve(events)]


def kpi_tiles(records: list[dict]) -> list[dict]:
    """Build top-level KPI tiles for the dashboard."""
    s = drill_summary(records)
    return [
        {"label": "Pulled SKUs", "value": s["verdicts"].get("PULL", 0)},
        {"label": "Hold/Verify SKUs", "value": s["verdicts"].get("HOLD_VERIFY", 0)},
        {"label": "Stores", "value": s["stores"]},
        {"label": "Allocations", "value": s["allocations"]},
    ]


def dashboard_data(
    records: list[dict],
    events: list[dict] | None = None,
    stores: list[Store] | None = None,
) -> DashboardModel:
    """Assemble a DashboardModel from plan records, simulation events, and stores."""
    playbooks = [r for r in records if r.get("type") == "store_playbook"]
    pts = map_points(stores or [], playbooks)
    tl = timeline_series(events or [])
    return DashboardModel(kpis=kpi_tiles(records), points=pts, timeline=tl)


def dashboard_to_json(model: DashboardModel) -> str:
    """Serialize a DashboardModel to JSON."""
    return json.dumps(asdict(model), indent=2, sort_keys=True)


def dashboard_html(model: DashboardModel) -> str:
    """Render a self-contained HTML dashboard view."""
    kpi_html = "".join(f"<div class='tile'><h3>{k['label']}</h3><p>{k['value']}</p></div>" for k in model.kpis)
    return f"<!DOCTYPE html><html><head><title>Recall Storm Dashboard</title></head><body><h1>Recall Storm</h1><section>{kpi_html}</section></body></html>"
