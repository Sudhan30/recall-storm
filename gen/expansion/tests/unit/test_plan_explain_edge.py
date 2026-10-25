"""Edge tests for recallstorm.plan.explain."""
from recallstorm.plan.explain import (
    explain_sku,
    plan_narrative,
)


def test_explain_edge():
    assert "UNKNOWN" in explain_sku({})
    assert "Recall Storm" in plan_narrative([])
