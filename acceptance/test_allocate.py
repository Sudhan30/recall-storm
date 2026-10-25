"""OURS. Hidden acceptance tests for recallstorm.allocate.allocate_substitutes (contract signature).

Contract: never exceed stock; integer cases; deterministic tie-breaks by store_id.
"""
from __future__ import annotations

import random
from collections import defaultdict

import pytest

alloc_mod = pytest.importorskip("recallstorm.allocate")


def allocate_substitutes(*a, **kw):
    fn = getattr(alloc_mod, "allocate_substitutes", None)
    assert fn is not None, "recallstorm.allocate must expose allocate_substitutes (contract)"
    return fn(*a, **kw)


def _store(sid, dc, fmt="SUPERCENTER"):
    from contract import Store, StoreFormat
    return Store(store_id=sid, format=StoreFormat(fmt), state="CA", city="X", lat=36.0, lon=-120.0,
                 district="D01", dc_id=dc, tz="America/Los_Angeles")


def _stock(dc, sku, cases):
    from contract import DcStock
    return DcStock(dc_id=dc, sku_id=sku, cases=cases)


def _check_invariants(allocs, demand, stock, stores):
    st = {(s.dc_id, s.sku_id): s.cases for s in stock}
    dc_of = {s.store_id: s.dc_id for s in stores}
    used = defaultdict(int)
    per_key = defaultdict(int)
    ids = set()
    for a in allocs:
        assert isinstance(a.qty_cases, int) and not isinstance(a.qty_cases, bool), f"non-integer {a.qty_cases!r}"
        assert a.qty_cases > 0, f"non-positive allocation {a}"
        assert a.alloc_id not in ids, f"duplicate alloc_id {a.alloc_id}"
        ids.add(a.alloc_id)
        assert (a.store_id, a.sub_sku_id) in demand, f"allocation without demand {a}"
        assert a.dc_id == dc_of[a.store_id], f"{a.store_id} is served by {dc_of[a.store_id]}, not {a.dc_id}"
        k = (a.dc_id, a.sub_sku_id)
        assert k in st, f"no stock row for {k}"
        used[k] += a.qty_cases
        assert a.dc_balance_after == st[k] - used[k], f"dc_balance_after {a.dc_balance_after} != {st[k] - used[k]}"
        assert a.dc_balance_after >= 0
        per_key[(a.store_id, a.sub_sku_id)] += a.qty_cases
    for k, u in used.items():
        assert u <= st[k], f"allocated {u} > stock {st[k]} for {k}"
    for k, q in per_key.items():
        assert q <= demand[k], f"allocated {q} > demand {demand[k]} for {k}"
    return used, per_key


def test_real_data_conservation_and_integers(pack, sub_demand):
    if not sub_demand:
        pytest.skip("no substitute demand in data")
    allocs = allocate_substitutes(dict(sub_demand), list(pack.dc_stock), list(pack.stores))
    used, _ = _check_invariants(allocs, sub_demand, pack.dc_stock, pack.stores)
    assert allocs, "no allocations at all"


def test_real_data_uses_available_stock(pack, sub_demand):
    """Demand is ~1.4x stock: every (dc, sub) should end with stock exhausted or demand met."""
    if not sub_demand:
        pytest.skip("no substitute demand in data")
    allocs = allocate_substitutes(dict(sub_demand), list(pack.dc_stock), list(pack.stores))
    used, _ = _check_invariants(allocs, sub_demand, pack.dc_stock, pack.stores)
    st = {(s.dc_id, s.sku_id): s.cases for s in pack.dc_stock}
    dc_of = {s.store_id: s.dc_id for s in pack.stores}
    want = defaultdict(int)
    for (sid, sub), q in sub_demand.items():
        want[(dc_of[sid], sub)] += q
    for k, w in want.items():
        assert used.get(k, 0) == min(w, st.get(k, 0)), f"{k}: allocated {used.get(k, 0)}, want {w}, stock {st.get(k, 0)}"


def test_demand_above_stock():
    stores = [_store("S1", "DC1"), _store("S2", "DC1"), _store("S3", "DC1")]
    demand = {("S1", "SUB"): 5, ("S2", "SUB"): 5, ("S3", "SUB"): 5}
    stock = [_stock("DC1", "SUB", 7)]
    allocs = allocate_substitutes(demand, stock, stores)
    used, _ = _check_invariants(allocs, demand, stock, stores)
    assert used[("DC1", "SUB")] == 7


def test_demand_below_stock_fully_met():
    stores = [_store("S1", "DC1"), _store("S2", "DC2")]
    demand = {("S1", "SUB"): 3, ("S2", "SUB"): 2}
    stock = [_stock("DC1", "SUB", 10), _stock("DC2", "SUB", 10)]
    allocs = allocate_substitutes(demand, stock, stores)
    _, per_key = _check_invariants(allocs, demand, stock, stores)
    assert per_key == {("S1", "SUB"): 3, ("S2", "SUB"): 2}


def test_stock_is_per_dc():
    """Stock at one DC never serves a store of another DC."""
    stores = [_store("S1", "DC1"), _store("S2", "DC2")]
    demand = {("S1", "SUB"): 4, ("S2", "SUB"): 4}
    stock = [_stock("DC1", "SUB", 8)]
    allocs = allocate_substitutes(demand, stock, stores)
    _, per_key = _check_invariants(allocs, demand, stock, stores)
    assert per_key.get(("S2", "SUB"), 0) == 0
    assert per_key.get(("S1", "SUB"), 0) == 4


def test_no_stock_row_means_no_allocation():
    stores = [_store("S1", "DC1")]
    allocs = allocate_substitutes({("S1", "MISSING"): 3}, [_stock("DC1", "OTHER", 5)], stores)
    assert [a for a in allocs if a.qty_cases > 0] == []


def test_empty_demand():
    assert list(allocate_substitutes({}, [_stock("DC1", "SUB", 5)], [_store("S1", "DC1")])) == []


def test_tie_break_by_store_id():
    stores = [_store("S2", "DC1"), _store("S1", "DC1"), _store("S3", "DC1")]
    demand = {("S3", "SUB"): 1, ("S2", "SUB"): 1, ("S1", "SUB"): 1}
    stock = [_stock("DC1", "SUB", 1)]
    allocs = allocate_substitutes(demand, stock, stores)
    _check_invariants(allocs, demand, stock, stores)
    got = [(a.store_id, a.qty_cases) for a in allocs if a.qty_cases > 0]
    assert got == [("S1", 1)], f"tie should go to the lowest store_id, got {got}"


def _canon(allocs):
    return sorted((a.dc_id, a.sub_sku_id, a.store_id, a.qty_cases) for a in allocs)


def test_deterministic_under_input_order(pack, sub_demand):
    if not sub_demand:
        pytest.skip("no substitute demand in data")
    a1 = allocate_substitutes(dict(sub_demand), list(pack.dc_stock), list(pack.stores))
    items = list(sub_demand.items()); random.Random(7).shuffle(items)
    stores = list(pack.stores); random.Random(8).shuffle(stores)
    stock = list(pack.dc_stock); random.Random(9).shuffle(stock)
    a2 = allocate_substitutes(dict(items), stock, stores)
    assert _canon(a1) == _canon(a2)
    a3 = allocate_substitutes(dict(sub_demand), list(pack.dc_stock), list(pack.stores))
    assert [(a.alloc_id, a.store_id, a.qty_cases) for a in a1] == [(a.alloc_id, a.store_id, a.qty_cases) for a in a3]
