"""Edge case tests for recallstorm.ingest.manifest_io."""
from recallstorm.ingest.manifest_io import filter_by_state, subset_skus
from tests.unit.test_ingest_manifest_io import _dummy_pack


def test_manifest_io_edge():
    pack = _dummy_pack()
    empty_state = filter_by_state(pack, "ZZ")
    assert len(empty_state.stores) == 0
    empty_skus = subset_skus(pack, set())
    assert len(empty_skus.skus) == 0
