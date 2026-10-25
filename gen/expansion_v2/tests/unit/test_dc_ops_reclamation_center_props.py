"""Property tests for recallstorm.dc_ops.reclamation_center."""
from recallstorm.dc_ops.reclamation_center import separate_hazmat_aerosols_and_lithium_ion


def test_separate_hazmat_partition_props():
    items = [{"sku_id": f"S{i}", "is_hazmat": (i % 3 == 0)} for i in range(18)]
    res = separate_hazmat_aerosols_and_lithium_ion(items)
    assert len(res["hazmat"]) + len(res["general"]) == 18
