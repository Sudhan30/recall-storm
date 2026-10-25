"""Edge case tests for recallstorm.rules.pfas_mn."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.pfas_mn import detect_pfas_claim, evaluate_pfas


def test_pfas_mn_edge():
    assert detect_pfas_claim("CERAMIC COATING (PFAS-FREE, PFOA-FREE)") is None
    sku = Sku("PF1", "00012345678905", "Pan", "B", "cookware", "PTFE", False, False, 6, 2.0, 12.0)
    assert evaluate_pfas(sku, "CA", datetime(2026, 1, 1)).verdict == Verdict.KEEP
