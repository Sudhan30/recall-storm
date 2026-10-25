"""Unit tests for recallstorm.ingest.manifest_io."""
from datetime import datetime
from contract import DataPack, Facing, Location, Rule, Sku, Store, StoreFormat
from recallstorm.ingest.manifest_io import (
    compare_datapacks,
    datapack_hash,
    datapack_stats,
    filter_by_state,
    filter_by_stores,
    sample_datapack,
    subset_skus,
    write_datapack,
)


def _dummy_pack() -> DataPack:
    s1 = Sku("S1", "00012345678905", "N1", "B", "c", "I", True, False, 12, 1.0, 5.0)
    s2 = Sku("S2", "00012345678912", "N2", "B", "c", "I", True, False, 12, 1.0, 5.0)
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.DISCOUNT, "NV", "Reno", 39.0, -119.0, "D02", "DC2", "America/Los_Angeles")
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    r1 = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "txt")
    return DataPack([s1, s2], [st1, st2], [f1], [], [], [], {"S1": ["S2"]}, [], [r1], datetime(2026, 12, 30))


def test_manifest_io(tmp_path):
    pack = _dummy_pack()
    stats = datapack_stats(pack)
    assert stats["skus"] == 2 and stats["stores"] == 2
    ca_pack = filter_by_state(pack, "CA")
    assert len(ca_pack.stores) == 1
    sub_pack = subset_skus(pack, {"S1"})
    assert len(sub_pack.skus) == 1
    sampled = sample_datapack(pack, max_stores=1, max_skus=1)
    assert len(sampled.stores) == 1 and len(sampled.skus) == 1
    assert datapack_hash(pack) == datapack_hash(pack)
    diff = compare_datapacks(ca_pack, pack)
    assert diff["stores"] == 1
    written = write_datapack(ca_pack, str(tmp_path / "out_pack"))
    assert written["stores"] == 1
    assert len(filter_by_stores(pack, {"WM1"}).stores) == 1
