"""Property tests for recallstorm.governance.board_reporting."""
import random
from recallstorm.governance.board_reporting import track_capex_investment_in_esl_and_epcis


def test_capex_investment_additive_props():
    rng = random.Random(42)
    for _ in range(25):
        a = round(rng.uniform(1.0, 50.0), 2)
        b = round(rng.uniform(1.0, 50.0), 2)
        assert track_capex_investment_in_esl_and_epcis(a, b) == round(a + b, 2)
