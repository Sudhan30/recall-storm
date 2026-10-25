"""Edge case tests for recallstorm.report.checks."""
from recallstorm.report.checks import check_capacity, check_conservation, check_contradictions


def test_report_checks_detect_violations():
    over_mnf = [
        {
            "type": "route_manifest",
            "manifest_id": "M1",
            "limits": {"cube_ft3": 100.0, "weight_lb": 1000.0},
            "stops": [{"store_id": "WM1", "cases": 50, "cube_ft3": 200.0, "weight_lb": 500.0}],
        }
    ]
    assert len(check_capacity(over_mnf)) == 1

    bad_alloc = [{"type": "allocation", "alloc_id": "A1", "dc_id": "DC1", "sub_sku_id": "S1", "qty_cases": 5, "dc_balance_after": -2}]
    assert len(check_conservation(bad_alloc)) == 1

    contrad = [
        {"type": "sku_verdict", "sku_id": "S1", "verdict": "KEEP"},
        {"type": "shelf_task", "task_id": "T1", "sku_id": "S1", "action": "PULL"},
    ]
    assert len(check_contradictions(contrad)) == 1
