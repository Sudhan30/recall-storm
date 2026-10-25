"""Property tests for recallstorm.rules.pfas_mn."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.pfas_mn import evaluate_pfas, pfas_product_categories


def test_pfas_categories_props():
    for cat in pfas_product_categories():
        sku = Sku("PF1", "00012345678905", "Item", "B", cat, "CONTAINS PTFE AND PFAS", False, False, 6, 1.0, 5.0)
        assert evaluate_pfas(sku, "MN", datetime(2026, 1, 1)).verdict == Verdict.PULL
