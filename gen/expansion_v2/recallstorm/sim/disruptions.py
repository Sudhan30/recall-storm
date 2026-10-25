"""Inject and replan around operational disruptions (absent staff, truck delays)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random

from contract import Store
from recallstorm.core.clock import iso_with_offset


@dataclass(frozen=True)
class Disruption:
    """Operational disruption event for stress-testing execution plans."""

    kind: str
    target_id: str
    details: dict = field(default_factory=dict)


@dataclass
class DisruptionSet:
    """Collection of simulated disruptions."""

    items: list[Disruption] = field(default_factory=list)


def absent_associate(associate_id: str, store_id: str) -> Disruption:
    """Create an ABSENT_ASSOCIATE disruption."""
    return Disruption(kind="ABSENT_ASSOCIATE", target_id=associate_id, details={"store_id": store_id})


def truck_delay(truck_id: str, delay_minutes: int) -> Disruption:
    """Create a TRUCK_DELAY disruption."""
    return Disruption(kind="TRUCK_DELAY", target_id=truck_id, details={"delay_minutes": int(delay_minutes)})


def stockout_event(dc_id: str, sku_id: str) -> Disruption:
    """Create a STOCKOUT disruption at a distribution center."""
    return Disruption(kind="STOCKOUT", target_id=dc_id, details={"sku_id": sku_id})


def inject_disruption(records: list[dict], disruption: Disruption) -> list[dict]:
    """Apply a Disruption to plan records."""
    out: list[dict] = []
    for r in records:
        rec = dict(r)
        if disruption.kind == "TRUCK_DELAY" and rec.get("type") == "route_manifest" and rec.get("truck_id") == disruption.target_id:
            dt = datetime.fromisoformat(rec["depart"]) + timedelta(minutes=int(disruption.details.get("delay_minutes", 30)))
            rec["depart"] = iso_with_offset(dt)
        out.append(rec)
    return out


def replan_after_disruption(
    records: list[dict], disruption: Disruption, backup_assoc_id: str = "BACKUP-A00"
) -> list[dict]:
    """Reassign tasks affected by an ABSENT_ASSOCIATE disruption to backup_assoc_id."""
    out: list[dict] = []
    for r in inject_disruption(records, disruption):
        rec = dict(r)
        if disruption.kind == "ABSENT_ASSOCIATE" and rec.get("type") == "shelf_task" and rec.get("associate_id") == disruption.target_id:
            rec["associate_id"] = backup_assoc_id
        out.append(rec)
    return out


def seed_disruptions(stores: list[Store], seed: int = 42) -> list[Disruption]:
    """Deterministically generate sample disruptions for stores."""
    rng = random.Random(int(seed))
    if not stores:
        return []
    chosen = rng.choice(sorted(stores, key=lambda s: s.store_id))
    return [absent_associate(f"{chosen.store_id}-A00", chosen.store_id)]


def disruption_report(disruptions: list[Disruption]) -> dict:
    """Summarize a list of Disruptions."""
    return {"count": len(disruptions), "kinds": [d.kind for d in disruptions]}
