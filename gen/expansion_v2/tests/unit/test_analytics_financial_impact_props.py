"""Property tests for recallstorm.analytics.financial_impact."""
import random
from recallstorm.analytics.financial_impact import generate_cfo_recall_financial_bridge


def test_cfo_bridge_accounting_identity():
    rng = random.Random(42)
    for _ in range(25):
        gross = round(rng.uniform(1000.0, 50000.0), 2)
        rec = round(rng.uniform(0.0, gross), 2)
        b = generate_cfo_recall_financial_bridge(gross, rec)
        assert abs((b["net_usd"] + b["recovered_usd"]) - b["gross_usd"]) <= 0.02
