"""Property tests for recallstorm.adjudicate.sampling."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.sampling import sample_for_review


def test_sampling_order_invariance():
    decs = [SkuDecision(f"S{i:02d}", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "") for i in range(20)]
    assert sample_for_review(decs, 0.25, 99) == sample_for_review(list(reversed(decs)), 0.25, 99)
