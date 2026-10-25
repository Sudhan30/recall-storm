"""Unit tests for recallstorm.ingest.manifest_io."""
from datetime import datetime, timezone
from contract import (
    Associate,
    DataPack,
    DcStock,
    Facing,
    Location,
    Rule,
    Sku,
    Store,
    StoreFormat,
    StoreNote,
    Truck,
)
from recallstorm.ingest.manifest_io import (
    compare_datapacks,
    datapack_hash,
    datapack_stats,
    filter_by_state,
    filter_by_stores,
    load_datapack_extended,
    sample_datapack,
    subset_skus,
    write_datapack,
)


def _make_pack() -> DataPack:
    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    sk1 = Sku("S1", "00012345678905", "N1", "B", "c", "SUGAR", True, False, 12, 1.0, 5.0)
    sk2 = Sku("S2", "00012345678912", "N2", "B", "c", "WATER", True, False, 12, 1.0, 5.0)
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.DISCOUNT, "NV", "Reno", 39.5, -119.8, "D02", "DC2", "America/Los_Angeles")
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    a1 = Associate("A1", "WM1", "D01", False, dt, dt)
    t1 = Truck("T1", "DC1", 3400.0, 40000.0, dt)
    d1 = DcStock("DC1", "S1", 5)
    n1 = StoreNote("N1", "WM1", "Endcap 1")
    r1 = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "src")
    return DataPack([sk1, sk2], [st1, st2], [f1], [a1], [t1], [d1], {"S1": ["S2"]}, [n1], [r1], dt)


def test_manifest_io_operations(tmp_path):
    pack = _make_pack()
    counts = write_datapack(pack, tmp_path)
    assert counts["skus"] == 2
    stats = datapack_stats(pack)
    assert stats["stores"] == 2
    ca_pack = filter_by_state(pack, "CA")
    assert len(ca_pack.stores) == 1
    st_pack = filter_by_stores(pack, ["WM1"])
    assert len(st_pack.stores) == 1
    sampled = sample_datapack(pack, 1, seed=7)
    assert len(sampled.stores) == 1
    sub = subset_skus(pack, ["S1"])
    assert len(sub.skus) == 1
    assert datapack_hash(pack) == datapack_hash(pack)
    diff = compare_datapacks(ca_pack, pack)
    assert diff["stores"] == 1
    loaded = load_datapack_extended("data")
    assert len(loaded.skus) > 0
