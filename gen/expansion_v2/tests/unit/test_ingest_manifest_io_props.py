"""Property tests for recallstorm.ingest.manifest_io."""
from recallstorm.ingest.manifest_io import datapack_hash, sample_datapack
from tests.unit.test_ingest_manifest_io import _dummy_pack


def test_manifest_io_props():
    pack = _dummy_pack()
    s1 = sample_datapack(pack, 1, 1)
    s2 = sample_datapack(pack, 1, 1)
    assert datapack_hash(s1) == datapack_hash(s2)
