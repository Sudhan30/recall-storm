"""Property tests for recallstorm.vendor.co_packer_traceability."""
from recallstorm.vendor.co_packer_traceability import (
    clear_unaffected_sister_plant_inventory,
    isolate_affected_co_packer_facility,
)


def test_isolate_and_clear_partition_lots():
    lots = [f"2610{i}CA" if i % 2 == 0 else f"2610{i}TX" for i in range(20)]
    affected = isolate_affected_co_packer_facility(lots, "CA")
    cleared = clear_unaffected_sister_plant_inventory(lots, "CA")
    assert len(affected) + len(cleared) == len(lots)
    assert set(affected).isdisjoint(set(cleared))
