"""Unit tests for recallstorm.route.pack_returns."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import pytest

from contract import PLAN_TYPES, Sku, Store, StoreFormat, Truck
from recallstorm.route import manifest_to_plan_record, pack_returns

_TZ = timezone(timedelta(hours=-8))
_DEPART = datetime(2026, 12, 31, 8, 0, 0, tzinfo=_TZ)


def _make_sku(sku_id: str, cube: float = 2.0, weight: float = 10.0) -> Sku:
    return Sku(
        sku_id=sku_id,
        gtin="00000000000001",
        name=f"Item {sku_id}",
        brand="Brand",
        category="candy",
        ingredients="SUGAR, RED 3",
        is_food=True,
        is_ingested_drug=False,
        case_units=12,
        case_cube_ft3=cube,
        case_weight_lb=weight,
    )


def _make_store(store_id: str, dc_id: str = "DC_NORTH") -> Store:
    return Store(
        store_id=store_id,
        format=StoreFormat.SUPERCENTER,
        state="CA",
        city="Sacramento",
        lat=38.58,
        lon=-121.49,
        district="D01",
        dc_id=dc_id,
        tz="America/Los_Angeles",
    )


def _make_truck(
    truck_id: str,
    dc_id: str = "DC_NORTH",
    cube: float = 100.0,
    weight: float = 1000.0,
    depart: datetime = _DEPART,
) -> Truck:
    return Truck(
        truck_id=truck_id,
        dc_id=dc_id,
        cube_ft3=cube,
        weight_lb=weight,
        depart=depart,
    )


def test_pack_returns_empty_and_zero_cases() -> None:
    skus = [_make_sku("SKU1")]
    stores = [_make_store("ST1")]
    trucks = [_make_truck("T1")]

    assert pack_returns({}, skus, trucks, stores) == []
    assert pack_returns({("ST1", "SKU1"): 0}, skus, trucks, stores) == []


def test_pack_returns_single_dc_fits_one_truck() -> None:
    skus = [_make_sku("SKU1", cube=2.5, weight=12.0), _make_sku("SKU2", cube=1.5, weight=8.0)]
    stores = [_make_store("ST1", "DC_NORTH"), _make_store("ST2", "DC_NORTH")]
    trucks = [_make_truck("DC_NORTH-T0", "DC_NORTH", cube=100.0, weight=1000.0)]

    pulled = {
        ("ST1", "SKU1"): 4,  # 10.0 ft3, 48.0 lb
        ("ST1", "SKU2"): 2,  # 3.0 ft3, 16.0 lb -> ST1: 6 cases, 13.0 ft3, 64.0 lb
        ("ST2", "SKU1"): 2,  # 5.0 ft3, 24.0 lb -> ST2: 2 cases, 5.0 ft3, 24.0 lb
    }
    manifests = pack_returns(pulled, skus, trucks, stores)
    assert len(manifests) == 1
    m = manifests[0]
    assert m.truck_id == "DC_NORTH-T0"
    assert m.dc_id == "DC_NORTH"
    assert m.depart == _DEPART
    assert len(m.stops) == 2
    assert m.stops[0].store_id == "ST1"
    assert m.stops[0].cases == 6
    assert m.stops[0].cube_ft3 == pytest.approx(13.0)
    assert m.stops[0].weight_lb == pytest.approx(64.0)
    assert m.stops[1].store_id == "ST2"
    assert m.stops[1].cases == 2
    assert m.stops[1].cube_ft3 == pytest.approx(5.0)
    assert m.stops[1].weight_lb == pytest.approx(24.0)


def test_pack_returns_splits_single_store_across_multiple_trucks() -> None:
    skus = [_make_sku("SKU_HEAVY", cube=10.0, weight=100.0)]
    stores = [_make_store("ST1", "DC_SOUTH")]
    trucks = [
        _make_truck("DC_SOUTH-T0", "DC_SOUTH", cube=35.0, weight=350.0),
        _make_truck("DC_SOUTH-T1", "DC_SOUTH", cube=35.0, weight=350.0),
        _make_truck("DC_SOUTH-T2", "DC_SOUTH", cube=35.0, weight=350.0),
    ]

    # 5 cases = 50 ft3, 500 lb -> 3 cases on T0, 2 cases on T1, T2 unused
    pulled = {("ST1", "SKU_HEAVY"): 5}
    manifests = pack_returns(pulled, skus, trucks, stores)

    assert len(manifests) == 2
    assert [m.truck_id for m in manifests] == ["DC_SOUTH-T0", "DC_SOUTH-T1"]
    assert sum(s.cases for m in manifests for s in m.stops) == 5
    for m, t in zip(manifests, trucks[:2]):
        assert len(m.stops) == 1
        assert m.stops[0].store_id == "ST1"
        assert m.stops[0].cube_ft3 <= t.cube_ft3
        assert m.stops[0].weight_lb <= t.weight_lb


def test_pack_returns_splits_when_fragmented_across_stores() -> None:
    skus = [_make_sku("SKU1", cube=10.0, weight=50.0)]
    stores = [
        _make_store("ST1", "DC_CENTRAL"),
        _make_store("ST2", "DC_CENTRAL"),
        _make_store("ST3", "DC_CENTRAL"),
    ]
    # 2 trucks, each holds 6 cases (60 ft3, 300 lb); 3 stores each have 4 cases (total 12 cases)
    trucks = [
        _make_truck("DC_CENTRAL-T0", "DC_CENTRAL", cube=60.0, weight=300.0),
        _make_truck("DC_CENTRAL-T1", "DC_CENTRAL", cube=60.0, weight=300.0),
    ]
    pulled = {
        ("ST1", "SKU1"): 4,
        ("ST2", "SKU1"): 4,
        ("ST3", "SKU1"): 4,
    }

    manifests = pack_returns(pulled, skus, trucks, stores)
    assert len(manifests) == 2
    assert {m.truck_id for m in manifests} == {"DC_CENTRAL-T0", "DC_CENTRAL-T1"}

    cases_by_store: dict[str, int] = {}
    for m in manifests:
        assert sum(s.cube_ft3 for s in m.stops) <= 60.0
        assert sum(s.weight_lb for s in m.stops) <= 300.0
        for s in m.stops:
            cases_by_store[s.store_id] = cases_by_store.get(s.store_id, 0) + s.cases
    assert cases_by_store == {"ST1": 4, "ST2": 4, "ST3": 4}


def test_pack_returns_respects_dc_isolation_and_determinism() -> None:
    skus = [_make_sku("SKU1", cube=2.0, weight=10.0)]
    stores = [
        _make_store("ST_N", "DC_NORTH"),
        _make_store("ST_S", "DC_SOUTH"),
    ]
    trucks = [
        _make_truck("DC_SOUTH-T0", "DC_SOUTH", cube=50.0, weight=500.0),
        _make_truck("DC_NORTH-T0", "DC_NORTH", cube=50.0, weight=500.0),
    ]
    pulled = {("ST_S", "SKU1"): 3, ("ST_N", "SKU1"): 5}

    m1 = pack_returns(pulled, skus, trucks, stores)
    m2 = pack_returns(pulled, list(reversed(skus)), list(reversed(trucks)), list(reversed(stores)))
    assert m1 == m2
    assert len(m1) == 2
    assert m1[0].dc_id == "DC_NORTH"
    assert m1[0].truck_id == "DC_NORTH-T0"
    assert m1[0].stops[0].store_id == "ST_N"
    assert m1[1].dc_id == "DC_SOUTH"
    assert m1[1].truck_id == "DC_SOUTH-T0"
    assert m1[1].stops[0].store_id == "ST_S"


def test_pack_returns_raises_on_insufficient_capacity() -> None:
    skus = [_make_sku("SKU1", cube=15.0, weight=100.0)]
    stores = [_make_store("ST1", "DC_NORTH")]
    trucks = [_make_truck("DC_NORTH-T0", "DC_NORTH", cube=20.0, weight=500.0)]

    with pytest.raises(ValueError, match="DC_NORTH"):
        pack_returns({("ST1", "SKU1"): 2}, skus, trucks, stores)


def test_manifest_to_plan_record_matches_contract_fields() -> None:
    sku = _make_sku("SKU1", cube=2.0, weight=10.0)
    store = _make_store("ST1", "DC_NORTH")
    truck = _make_truck("DC_NORTH-T0", "DC_NORTH", cube=100.0, weight=1000.0)
    manifests = pack_returns({("ST1", "SKU1"): 3}, [sku], [truck], [store])

    rec = manifest_to_plan_record(manifests[0], truck)
    assert rec["type"] == "route_manifest"
    for field_name in PLAN_TYPES["route_manifest"]:
        assert field_name in rec
