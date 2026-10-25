"""Unit tests for recallstorm.plan."""
from __future__ import annotations

from datetime import datetime
from contract import (
    Associate,
    DataPack,
    DcStock,
    Facing,
    Location,
    PLAN_TYPES,
    Rule,
    Sku,
    Store,
    StoreFormat,
    StoreNote,
    Truck,
)
from recallstorm.plan import build_plan, pack_returns


def _sample_datapack() -> DataPack:
    skus = [
        Sku("SKU_PULL", "0001", "Candy Red 3", "BrandA", "candy", "sugar, FD&C Red No. 3", True, False, 12, 1.0, 10.0),
        Sku("SKU_HOLD", "0002", "Frosting Unclear", "BrandA", "frosting", "sugar, color added", True, False, 12, 0.8, 8.0),
        Sku("SKU_SUB", "0003", "Candy Safe", "BrandA", "candy", "sugar, salt, red 40", True, False, 12, 1.0, 10.0),
    ]
    stores = [
        Store("CA1000", StoreFormat.SUPERCENTER, "CA", "Sacramento", 38.5, -121.5, "D01", "DC_NORTH", "America/Los_Angeles"),
    ]
    facings = [
        Facing("CA1000", "SKU_PULL", Location("A01", 1, 1, 1), 24),
        Facing("CA1000", "SKU_HOLD", Location("A01", 2, 1, 1), 12),
    ]
    associates = [
        Associate(
            "CA1000-A00",
            "CA1000",
            "D01",
            False,
            datetime.fromisoformat("2026-12-30T22:00:00-08:00"),
            datetime.fromisoformat("2026-12-31T06:00:00-08:00"),
        ),
    ]
    trucks = [
        Truck("DC_NORTH-T0", "DC_NORTH", 3400.0, 40000.0, datetime.fromisoformat("2026-12-31T08:00:00-08:00")),
    ]
    dc_stock = [
        DcStock("DC_NORTH", "SKU_SUB", 5),
    ]
    substitutes = {"SKU_PULL": ["SKU_SUB"]}
    notes = [
        StoreNote("N0000", "CA1000", "Endcap 1 holds a vendor Halloween display; candy there is not on the planogram."),
    ]
    rules = [
        Rule(
            "CA_AB418_RED3",
            "RED3",
            ("FD&C Red No. 3", "Red 3"),
            ("CA",),
            ("food",),
            datetime.fromisoformat("2027-01-01T00:00:00"),
            "Cal. Health & Safety Code 109025(a)",
            "Commencing January 1, 2027, Red dye 3 is prohibited.",
        )
    ]
    return DataPack(
        skus=skus,
        stores=stores,
        facings=facings,
        associates=associates,
        trucks=trucks,
        dc_stock=dc_stock,
        substitutes=substitutes,
        notes=notes,
        rules=rules,
        as_of=datetime.fromisoformat("2026-12-30T18:00:00-08:00"),
    )


def test_pack_returns_respects_limits() -> None:
    pack = _sample_datapack()
    pulled = {("CA1000", "SKU_PULL"): 10}
    manifests = pack_returns(pulled, pack.skus, pack.trucks, pack.stores)
    assert len(manifests) == 1
    m = manifests[0]
    assert m.dc_id == "DC_NORTH"
    assert len(m.stops) == 1
    assert m.stops[0].store_id == "CA1000"
    assert m.stops[0].cases == 10
    assert m.stops[0].cube_ft3 == 10.0
    assert m.stops[0].weight_lb == 100.0


def test_build_plan_emits_valid_records_and_respects_deadline() -> None:
    pack = _sample_datapack()
    scenario = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    records = build_plan(pack, scenario)
    deadline_dt = datetime.fromisoformat(scenario["deadline"])

    seen_types = {r["type"] for r in records}
    assert "run" in seen_types
    assert "sku_verdict" in seen_types
    assert "evidence" in seen_types
    assert "shelf_task" in seen_types
    assert "allocation" in seen_types
    assert "store_playbook" in seen_types
    assert "exception" in seen_types
    assert "route_manifest" in seen_types

    for rec in records:
        rtype = rec["type"]
        assert rtype in PLAN_TYPES
        for req_field in PLAN_TYPES[rtype]:
            assert req_field in rec
        assert rec["src"].endswith(".py")
        if "window" in rec:
            w_start = datetime.fromisoformat(rec["window"][0])
            w_end = datetime.fromisoformat(rec["window"][1])
            assert w_start <= w_end
            assert w_end < deadline_dt
