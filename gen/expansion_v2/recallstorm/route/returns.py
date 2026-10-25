"""Convert pulled shelf units/cases into store return loads with cube and weight."""
from __future__ import annotations

from dataclasses import dataclass
import math

from contract import Facing, Sku, SkuDecision, Stop, Store, Verdict


@dataclass(frozen=True)
class ReturnLoad:
    """Return load for a store and SKU."""

    store_id: str
    sku_id: str
    cases: int
    cube_ft3: float
    weight_lb: float


def case_cube(sku: Sku, cases: int = 1) -> float:
    """Calculate total cubic feet for cases of sku."""
    if cases < 0:
        raise ValueError("cases cannot be negative")
    return round(float(cases) * float(sku.case_cube_ft3), 4)


def case_weight(sku: Sku, cases: int = 1) -> float:
    """Calculate total weight in pounds for cases of sku."""
    if cases < 0:
        raise ValueError("cases cannot be negative")
    return round(float(cases) * float(sku.case_weight_lb), 4)


def returned_cases(
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    skus: dict[str, Sku],
    dsd_stores: set[str] | None = None,
) -> dict[tuple[str, str], int]:
    """Compute (store_id, sku_id) -> integer return cases for all PULL facings (excluding DSD stores if specified)."""
    excluded = dsd_stores or set()
    units_by_store_sku: dict[tuple[str, str], int] = {}
    for f in facings:
        if f.store_id in excluded or f.units <= 0:
            continue
        dec = decisions.get(f.sku_id)
        if dec and dec.verdict == Verdict.PULL:
            key = (f.store_id, f.sku_id)
            units_by_store_sku[key] = units_by_store_sku.get(key, 0) + f.units

    out: dict[tuple[str, str], int] = {}
    for (store_id, sku_id), units in sorted(units_by_store_sku.items()):
        sku = skus.get(sku_id)
        cu = max(1, sku.case_units if sku else 12)
        cases = int(math.ceil(units / cu))
        if cases > 0:
            out[(store_id, sku_id)] = cases
    return out


def cases_by_store(pulled_cases: dict[tuple[str, str], int]) -> dict[str, int]:
    """Sum pulled return cases per store_id."""
    out: dict[str, int] = {}
    for (st_id, _), cases in pulled_cases.items():
        if int(cases) > 0:
            out[st_id] = out.get(st_id, 0) + int(cases)
    return out


def cases_by_dc(pulled_cases: dict[tuple[str, str], int], stores: list[Store]) -> dict[str, int]:
    """Sum pulled return cases per dc_id."""
    st_to_dc = {s.store_id: s.dc_id for s in stores}
    out: dict[str, int] = {}
    for (st_id, _), cases in pulled_cases.items():
        dc_id = st_to_dc.get(st_id)
        if dc_id and int(cases) > 0:
            out[dc_id] = out.get(dc_id, 0) + int(cases)
    return out


def returns_to_stops(pulled_cases: dict[tuple[str, str], int], skus: dict[str, Sku]) -> list[Stop]:
    """Aggregate pulled_cases by store_id into Stop objects."""
    by_store: dict[str, list[tuple[str, int]]] = {}
    for (st_id, sku_id), cases in sorted(pulled_cases.items()):
        if int(cases) > 0:
            by_store.setdefault(st_id, []).append((sku_id, int(cases)))

    stops: list[Stop] = []
    for st_id in sorted(by_store.keys()):
        tot_cases = 0
        tot_cube = 0.0
        tot_weight = 0.0
        for sku_id, c in by_store[st_id]:
            sku = skus.get(sku_id)
            tot_cases += c
            tot_cube += c * (sku.case_cube_ft3 if sku else 1.5)
            tot_weight += c * (sku.case_weight_lb if sku else 10.0)
        stops.append(Stop(store_id=st_id, cases=tot_cases, cube_ft3=round(tot_cube, 4), weight_lb=round(tot_weight, 4)))
    return stops


def validate_returns(pulled_cases: dict[tuple[str, str], int], skus: dict[str, Sku]) -> list[str]:
    """Validate that pulled_cases has non-negative counts and known SKUs."""
    issues: list[str] = []
    for (st_id, sku_id), cases in pulled_cases.items():
        if int(cases) < 0:
            issues.append(f"Negative pulled cases for {st_id}/{sku_id}")
        if sku_id not in skus:
            issues.append(f"Unknown SKU {sku_id} in pulled_cases")
    return issues


def returns_summary(pulled_cases: dict[tuple[str, str], int], skus: dict[str, Sku]) -> dict:
    """Summarize total return cases, cube, and weight."""
    stops = returns_to_stops(pulled_cases, skus)
    return {
        "store_count": len(stops),
        "total_cases": sum(s.cases for s in stops),
        "total_cube_ft3": round(sum(s.cube_ft3 for s in stops), 2),
        "total_weight_lb": round(sum(s.weight_lb for s in stops), 2),
    }
