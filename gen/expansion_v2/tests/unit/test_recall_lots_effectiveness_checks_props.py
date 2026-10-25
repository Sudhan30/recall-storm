"""Property tests for recallstorm.recall_lots.effectiveness_checks."""
from recallstorm.recall_lots.effectiveness_checks import select_fda_level_a_through_e_sample


def test_fda_level_hierarchy_props():
    stores = [f"WM{i:03d}" for i in range(50)]
    sa = select_fda_level_a_through_e_sample("A", stores)
    sb = select_fda_level_a_through_e_sample("B", stores)
    sc = select_fda_level_a_through_e_sample("C", stores)
    se = select_fda_level_a_through_e_sample("E", stores)
    assert len(sa) > len(sb) > len(sc) > len(se) == 0
