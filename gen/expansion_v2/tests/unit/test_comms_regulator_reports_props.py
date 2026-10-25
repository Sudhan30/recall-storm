"""Property tests for recallstorm.comms.regulator_reports."""
import random
from recallstorm.comms.regulator_reports import compile_fda_district_recall_status_report


def test_status_report_percentage_bounds():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(1, 100)
        done = rng.randint(0, tot)
        res = compile_fda_district_recall_status_report("R1", done, tot)
        assert 0.0 <= res["pct"] <= 100.0
