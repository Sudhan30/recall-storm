"""OURS. Hidden acceptance tests for recallstorm.route.pack_returns (contract signature).

Contract: cube and weight within truck limits; every pulled case on exactly one stop.
"""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from conftest import make_sku

route_mod = pytest.importorskip("recallstorm.route")


def pack_returns(*a, **kw):
    fn = getattr(route_mod, "pack_returns", None)
    assert fn is not None, "recallstorm.route must expose pack_returns (contract)"
    return fn(*a, **kw)


DEP = datetime(2026, 12, 31, 8, 0, tzinfo=ZoneInfo("America/Los_Angeles"))


def _truck(tid, dc, cube=3400.0, weight=40000.0):
    from contract import Truck
    return Truck(truck_id=tid, dc_id=dc, cube_ft3=cube, weight_lb=weight, depart=DEP)


def _store(sid, dc):
    from contract import Store, StoreFormat
    return Store(store_id=sid, format=StoreFormat.SUPERCENTER, state="CA", city="X", lat=36.0, lon=-120.0,
                 district="D01", dc_id=dc, tz="America/Los_Angeles")


def _check(manifests, pulled, skus, trucks, stores):
    tr = {t.truck_id: t for t in trucks}
    sk = {s.sku_id: s for s in skus}
    dc_of = {s.store_id: s.dc_id for s in stores}
    seen_trucks, seen_ids = set(), set()
    got_cases, got_cube, got_wt = defaultdict(int), defaultdict(float), defaultdict(float)
    for m in manifests:
        assert m.manifest_id not in seen_ids, f"duplicate manifest_id {m.manifest_id}"
        seen_ids.add(m.manifest_id)
        assert m.truck_id in tr, f"unknown truck {m.truck_id}"
        assert m.truck_id not in seen_trucks, f"truck {m.truck_id} used twice"
        seen_trucks.add(m.truck_id)
        t = tr[m.truck_id]
        assert m.dc_id == t.dc_id
        assert len(m.stops) > 0, f"empty manifest {m.manifest_id}"
        cube = sum(s.cube_ft3 for s in m.stops); wt = sum(s.weight_lb for s in m.stops)
        assert cube <= t.cube_ft3 + 1e-6, f"{m.truck_id} cube {cube} > {t.cube_ft3}"
        assert wt <= t.weight_lb + 1e-6, f"{m.truck_id} weight {wt} > {t.weight_lb}"
        for s in m.stops:
            assert isinstance(s.cases, int) and s.cases > 0, f"bad stop cases {s.cases!r}"
            assert dc_of[s.store_id] == m.dc_id, f"stop {s.store_id} on another DC's truck"
            got_cases[s.store_id] += s.cases; got_cube[s.store_id] += s.cube_ft3; got_wt[s.store_id] += s.weight_lb
    want_cases, want_cube, want_wt = defaultdict(int), defaultdict(float), defaultdict(float)
    for (sid, sku), n in pulled.items():
        want_cases[sid] += n; want_cube[sid] += n * sk[sku].case_cube_ft3; want_wt[sid] += n * sk[sku].case_weight_lb
    assert dict(got_cases) == {k: v for k, v in want_cases.items() if v}, "every pulled case on exactly one stop"
    for sid in want_cases:
        assert abs(got_cube[sid] - want_cube[sid]) <= 0.01 * max(1.0, want_cube[sid]) + 0.05, \
            f"{sid} cube {got_cube[sid]} != {want_cube[sid]}"
        assert abs(got_wt[sid] - want_wt[sid]) <= 0.01 * max(1.0, want_wt[sid]) + 0.05, \
            f"{sid} weight {got_wt[sid]} != {want_wt[sid]}"


def test_real_data(pack, pulled_cases):
    if not pulled_cases:
        pytest.skip("no pulled cases in data")
    ms = pack_returns(dict(pulled_cases), list(pack.skus), list(pack.trucks), list(pack.stores))
    _check(ms, pulled_cases, pack.skus, pack.trucks, pack.stores)


def test_split_across_trucks_when_one_is_full():
    skus = [make_sku("x", sku_id="BIG", cube=2.0, weight=5.0)]
    stores = [_store("S1", "DC1")]
    trucks = [_truck("T0", "DC1"), _truck("T1", "DC1"), _truck("T2", "DC1")]
    pulled = {("S1", "BIG"): 3000}                      # 6000 ft3 > 3400 per truck
    ms = pack_returns(pulled, skus, trucks, stores)
    _check(ms, pulled, skus, trucks, stores)
    assert len(ms) >= 2


def test_weight_limit_binds():
    skus = [make_sku("x", sku_id="HEAVY", cube=0.5, weight=60.0)]
    stores = [_store("S1", "DC1"), _store("S2", "DC1")]
    trucks = [_truck("T0", "DC1"), _truck("T1", "DC1")]
    pulled = {("S1", "HEAVY"): 400, ("S2", "HEAVY"): 400}  # 48,000 lb > 40,000 per truck
    ms = pack_returns(pulled, skus, trucks, stores)
    _check(ms, pulled, skus, trucks, stores)


def test_dcs_kept_separate():
    skus = [make_sku("x", sku_id="A", cube=1.0, weight=10.0)]
    stores = [_store("N1", "DC_N"), _store("S1", "DC_S")]
    trucks = [_truck("TN", "DC_N"), _truck("TS", "DC_S")]
    pulled = {("N1", "A"): 10, ("S1", "A"): 20}
    ms = pack_returns(pulled, skus, trucks, stores)
    _check(ms, pulled, skus, trucks, stores)


def test_no_empty_manifests_with_spare_trucks():
    skus = [make_sku("x", sku_id="A", cube=1.0, weight=10.0)]
    stores = [_store("S1", "DC1")]
    trucks = [_truck(f"T{i}", "DC1") for i in range(6)]
    ms = pack_returns({("S1", "A"): 5}, skus, trucks, stores)
    _check(ms, {("S1", "A"): 5}, skus, trucks, stores)
    assert len(ms) == 1


def test_nothing_pulled():
    assert list(pack_returns({}, [make_sku("x", sku_id="A")], [_truck("T0", "DC1")], [_store("S1", "DC1")])) == []


def test_deterministic(pack, pulled_cases):
    if not pulled_cases:
        pytest.skip("no pulled cases in data")
    a = pack_returns(dict(pulled_cases), list(pack.skus), list(pack.trucks), list(pack.stores))
    items = list(pulled_cases.items()); random.Random(3).shuffle(items)
    trucks = list(pack.trucks); random.Random(4).shuffle(trucks)
    b = pack_returns(dict(items), list(pack.skus), trucks, list(pack.stores))
    canon = lambda ms: sorted((m.dc_id, tuple(sorted((s.store_id, s.cases) for s in m.stops))) for m in ms)
    assert canon(a) == canon(b)
