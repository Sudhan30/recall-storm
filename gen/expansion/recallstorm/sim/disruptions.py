"""Operational disruption injection (absent associates, truck delays, DC stockouts) and replanning."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import timedelta
from contract import DataPack, DcStock, Truck


@dataclass(frozen=True)
class Disruption:
    """Represents a simulated operational disruption."""

    kind: str
    target_id: str
    secondary_id: str | None = None
    delay_minutes: int = 0


@dataclass(frozen=True)
class DisruptionSet:
    """Collection of simulated disruptions."""

    items: tuple[Disruption, ...]


def absent_associate(associate_id: str) -> Disruption:
    """Create an ABSENT_ASSOCIATE disruption."""
    if not associate_id.strip():
        raise ValueError("associate_id must be non-empty")
    return Disruption(kind="ABSENT_ASSOCIATE", target_id=associate_id.strip())


def truck_delay(truck_id: str, delay_minutes: int = 60) -> Disruption:
    """Create a TRUCK_DELAY disruption."""
    if not truck_id.strip() or delay_minutes <= 0:
        raise ValueError("truck_id must be non-empty and delay_minutes > 0")
    return Disruption(kind="TRUCK_DELAY", target_id=truck_id.strip(), delay_minutes=delay_minutes)


def stockout_event(dc_id: str, sku_id: str) -> Disruption:
    """Create a DC_STOCKOUT disruption zeroing out a substitute SKU at a DC."""
    if not dc_id.strip() or not sku_id.strip():
        raise ValueError("dc_id and sku_id must be non-empty")
    return Disruption(kind="DC_STOCKOUT", target_id=dc_id.strip(), secondary_id=sku_id.strip())


def inject_disruption(pack: DataPack, disruption: Disruption) -> DataPack:
    """Return a new DataPack with the disruption applied."""
    if not isinstance(pack, DataPack) or not isinstance(disruption, Disruption):
        raise TypeError("Expected DataPack and Disruption")
    associates = list(pack.associates)
    trucks = list(pack.trucks)
    dc_stock = list(pack.dc_stock)

    if disruption.kind == "ABSENT_ASSOCIATE" and len(associates) > 1:
        associates = [a for a in associates if a.associate_id != disruption.target_id]
    elif disruption.kind == "TRUCK_DELAY":
        trucks = [
            Truck(
                t.truck_id,
                t.dc_id,
                t.cube_ft3,
                t.weight_lb,
                t.depart + timedelta(minutes=disruption.delay_minutes),
            )
            if t.truck_id == disruption.target_id
            else t
            for t in trucks
        ]
    elif disruption.kind == "DC_STOCKOUT":
        dc_stock = [
            DcStock(d.dc_id, d.sku_id, 0)
            if (d.dc_id == disruption.target_id and d.sku_id == disruption.secondary_id)
            else d
            for d in dc_stock
        ]

    return DataPack(
        skus=list(pack.skus),
        stores=list(pack.stores),
        facings=list(pack.facings),
        associates=associates,
        trucks=trucks,
        dc_stock=dc_stock,
        substitutes=dict(pack.substitutes),
        notes=list(pack.notes),
        rules=list(pack.rules),
        as_of=pack.as_of,
    )


def replan_after_disruption(pack: DataPack, scenario: dict, disruption: Disruption) -> list[dict]:
    """Inject a disruption into pack and re-assemble the recall execution plan."""
    from recallstorm.plan.assemble import assemble_plan
    perturbed = inject_disruption(pack, disruption)
    return assemble_plan(perturbed, scenario)


def seed_disruptions(pack: DataPack, seed: int = 42) -> list[Disruption]:
    """Deterministically generate a sample set of disruptions from a DataPack."""
    rng = random.Random(seed)
    out: list[Disruption] = []
    if pack.associates:
        a = rng.choice(pack.associates)
        out.append(absent_associate(a.associate_id))
    if pack.trucks:
        t = rng.choice(pack.trucks)
        out.append(truck_delay(t.truck_id, 45))
    if pack.dc_stock:
        d = rng.choice(pack.dc_stock)
        out.append(stockout_event(d.dc_id, d.sku_id))
    return out


def disruption_report(disruptions: list[Disruption]) -> dict:
    """Summarize disruptions by kind."""
    by_kind: dict[str, int] = {}
    for d in disruptions:
        by_kind[d.kind] = by_kind.get(d.kind, 0) + 1
    return {"total": len(disruptions), "by_kind": by_kind}
