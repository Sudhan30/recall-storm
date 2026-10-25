"""Dashboard data model, store status map points, KPI tiles, and self-contained HTML rendering."""
from __future__ import annotations

import json
from dataclasses import dataclass
from contract import Store
from recallstorm.report.summary import drill_summary
from recallstorm.sim.metrics import completion_curve


@dataclass(frozen=True)
class DashboardModel:
    """Dashboard payload container."""

    kpis: tuple[dict, ...]
    map_points: tuple[dict, ...]


@dataclass(frozen=True)
class DashboardBuilder:
    """Builds dashboard data and HTML from plan and event records."""

    title: str = "Recall Storm Command Center"


def store_status_colors(playbooks: list[dict]) -> dict[str, str]:
    """Assign status colors ('green', 'amber') to stores based on exception count."""
    colors: dict[str, str] = {}
    for p in playbooks:
        st_id = str(p.get("store_id", ""))
        excs = p.get("exception_ids", [])
        colors[st_id] = "amber" if excs else "green"
    return colors


def map_points(stores: list[Store], playbooks: list[dict]) -> list[dict]:
    """Build geographic map pin dictionaries for stores."""
    pb_by_store = {str(p.get("store_id")): p for p in playbooks}
    colors = store_status_colors(playbooks)
    out: list[dict] = []
    for s in sorted(stores, key=lambda x: x.store_id):
        pb = pb_by_store.get(s.store_id, {})
        out.append(
            {
                "store_id": s.store_id,
                "city": s.city,
                "format": s.format.value,
                "lat": s.lat,
                "lon": s.lon,
                "tasks": pb.get("counts", {}).get("total_tasks", 0),
                "color": colors.get(s.store_id, "green"),
            }
        )
    return out


def timeline_series(events: list[dict]) -> list[dict]:
    """Convert completion_curve into [{'t': iso, 'done': count}, ...] series."""
    return [{"t": t, "done": c} for t, c in completion_curve(events)]


def kpi_tiles(records: list[dict], events: list[dict]) -> list[dict]:
    """Build top-level KPI tile dictionaries for the command dashboard."""
    s = drill_summary(records)
    done_count = sum(1 for e in events if e.get("kind") == "DONE")
    return [
        {"label": "SKUs Pulled", "value": s["verdicts"].get("PULL", 0)},
        {"label": "SKUs Hold/Verify", "value": s["verdicts"].get("HOLD_VERIFY", 0)},
        {"label": "Stores Active", "value": s["stores"]},
        {"label": "Tasks Completed", "value": done_count},
    ]


def dashboard_data(records: list[dict], events: list[dict], stores: list[Store]) -> dict:
    """Assemble the complete dashboard data dictionary."""
    playbooks = [r for r in records if r.get("type") == "store_playbook"]
    return {
        "kpis": kpi_tiles(records, events),
        "map_points": map_points(stores, playbooks),
        "timeline": timeline_series(events),
    }


def dashboard_to_json(data: dict) -> str:
    """Serialize dashboard data to JSON."""
    return json.dumps(data, indent=2, sort_keys=True)


def dashboard_html(data: dict) -> str:
    """Render a self-contained HTML command dashboard page."""
    tiles_html = "".join(
        f"<div class='tile'><h3>{t['label']}</h3><p>{t['value']}</p></div>"
        for t in data.get("kpis", [])
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Recall Storm Dashboard</title></head>"
        f"<body><h1>Recall Storm Command Center</h1><div class='kpis'>{tiles_html}</div></body></html>"
    )
