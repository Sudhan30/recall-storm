"""Property tests for recallstorm.rules.model."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.model import ruleset_hash


def test_ruleset_hash_order_invariance():
    r1 = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c1", "t1")
    r2 = Rule("R2", "BVO", ("BVO",), ("US",), ("food",), datetime(2027, 1, 1), "c2", "t2")
    assert ruleset_hash([r1, r2]) == ruleset_hash([r2, r1])
