"""Edge case tests for recallstorm.plan.explain."""
from recallstorm.plan.explain import explain_allocation, explain_route, plan_narrative


def test_plan_explain_edge():
    assert plan_narrative([]) == "Plan Summary: "
    assert "ALC-2" in explain_allocation({"alloc_id": "ALC-2", "qty_cases": 1, "sub_sku_id": "S", "dc_id": "D", "store_id": "W"})
    assert "MNF-2" in explain_route({"manifest_id": "MNF-2", "truck_id": "T", "dc_id": "D", "stops": []})
