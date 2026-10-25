"""Edge case tests for recallstorm.rules.preemption."""
from datetime import datetime
from contract import Rule
from recallstorm.rules.preemption import effective_conflict, preemption_status


def test_preemption_edge():
    r1 = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 15), "ref", "txt")
    r2 = Rule("R2", "RED3", ("Red 3",), ("US",), ("food",), datetime(2027, 1, 15), "ref", "txt")
    r_drug = Rule("R3", "RED3", ("Red 3",), ("US",), ("ingested_drug",), datetime(2028, 1, 18), "ref", "txt")
    assert preemption_status(r1, r2) == "CONCURRENT"
    assert not effective_conflict(r1, r_drug)
