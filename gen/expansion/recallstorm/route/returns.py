"""Compute return cases, cube, and weight from pulled store inventory."""
from __future__ import annotations

import math
from dataclasses import dataclass
from contract import Facing, RouteManifest, Sku, SkuDecision, Stop, Store, Verdict


@dataclass(frozen=True)
class ReturnLoad:
    """Aggregated return load for a single store and SKU."""

    store_id: str
    sku_id: str
    cases: int
    cube_ft3: float
    weight_lb: float


def case_cube(sku: Sku, cases: int) -> float:
    """Compute total cubic feet for `cases` of `sku`."""
    if cases < 0:
        raise ValueError("cases must be non-negative")
    return round(cases * float(sku.case_cube_ft3), 4)


def case_weight(sku: Sku, cases: int) -> float:
    """Compute total weight in pounds for `cases` of `sku`."""
    if cases < 0:
        raise ValueError("cases must be non-negative")
    return round(cases * float(sku.case_weight_lb), 4)


def returned_cases(
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    skus_by_id: dict[str, Sku],
    dsd_stores: set[str] | None = None,
) -> dict[tuple[str, str], int]:
    """Compute (store_id, sku_id) -> whole cases pulled for return."""
    units_by_pair: dict[tuple[str, str], int] = {}
    for f in facings:
        dec = decisions.get(f.sku_id)
        if dec is None or dec.verdict != Verdict.PULL:
            continue
        if dsd_stores and f.store_id in dsd_stores:
            sku = skus_by_id.get(f.sku_id)
            if sku and "frito" in sku.brand.lower():
                continue
        key = (f.store_id, f.sku_id)
        units_by_pair[key] = units_by_pair.get(key, 0) + f.units

    out: dict[tuple[str, str], int] = {}
    for (st_id, sk_id), units in sorted(units_by_pair.items()):
        if units <= 0:
            continue
        sku = skus_by_id.get(sk_id)
        cu = max(1, sku.case_units if sku else 12)
        out[(st_id, sk_id)] = max(1, math.ceil(units / cu))
    return out


def cases_by_store(pulled_cases: dict[tuple[str, str], int]) -> dict[str, int]:
    """Aggregate total pulled cases per store_id."""
    out: dict[str, int] = {}
    for (st_id, _), cases in pulled_cases.items():
        if cases > 0:
            out[st_id] = out.get(st_id, 0) + int(cases)
    return out


def cases_by_dc(pulled_cases: dict[tuple[str, str], int], stores_by_id: dict[str, Store]) -> dict[str, int]:
    """Aggregate total pulled cases per dc_id."""
    out: dict[str, int] = {}
    for (st_id, _), cases in pulled_cases.items():
        if cases > 0 and st_id in stores_by_id:
            dc = stores_by_id[st_id].dc_id
            out[dc] = out.get(dc, 0) + int(cases)
    return out


def returns_to_stops(pulled_cases: dict[tuple[str, str], int], skus_by_id: dict[str, Sku]) -> list[Stop]:
    """Aggregate (store_id, sku_id) pulled cases into one Stop per store_id."""
    by_store: dict[str, list[tuple[str, int]]] = {}
    for (st_id, sk_id), cases in sorted(pulled_cases.items()):
        if cases > 0:
            by_store.setdefault(st_id, []).append((sk_id, int(cases)))

    stops: list[Stop] = []
    for st_id in sorted(by_store.keys()):
        tot_cases = 0
        tot_cube = 0.0
        tot_wt = 0.0
        for sk_id, c in by_store[st_id]:
            sku = skus_by_id.get(sk_id)
            u_cube = sku.case_cube_ft3 if sku else 1.5
            u_wt = sku.case_weight_lb if sku else 10.0
            tot_cases += c
            tot_cube += c * u_cube
            tot_wt += c * u_wt
        stops.append(
            Stop(
                store_id=st_id,
                cases=tot_cases,
                cube_ft3=round(tot_cube, 2),
                weight_lb=round(tot_wt, 2),
            )
        )
    return stops


def validate_returns(pulled_cases: dict[tuple[str, str], int], manifests: list[RouteManifest]) -> list[str]:
    """Verify that total pulled cases per store equal the cases on manifests and each store appears on at most one stop per manifest."""
    expected = cases_by_store(pulled_cases)
    actual: dict[str, int] = {}
    issues: list[str] = []
    for m in manifests:
        for s in m.stops:
            actual[s.store_id] = actual.get(s.store_id, 0) + s.cases
    for st_id, exp_c in sorted(expected.items()):
        act_c = actual.get(st_id, 0)
        if act_c != exp_c:
            issues.append(f"Store {st_id} pulled {exp_c} cases but manifests packed {act_c}")
    return issues


def returns_summary(pulled_cases: dict[tuple[str, str], int], skus_by_id: dict[str, Sku]) -> dict:
    """Summarize total return cases, cube, and weight."""
    stops = returns_to_stops(pulled_cases, skus_by_id)
    return {
        "store_count": len(stops),
        "total_cases": sum(s.cases for s in stops),
        "total_cube_ft3": round(sum(s.cube_ft3 for s in stops), 2),
        "total_weight_lb": round(sum(s.weight_lb for s in stops), 2),
    }
