"""Unit tests for recallstorm.adjudicate.sampling."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.sampling import (
    SampleSet,
    confidence_interval,
    estimate_error_rate,
    resample,
    review_rate,
    sample_for_review,
    sample_report,
    seed_sampler,
    stratified_sample,
)


def test_sampling():
    decs = [
        SkuDecision(f"S{i}", Verdict.PULL if i % 2 == 0 else Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "")
        for i in range(10)
    ]
    assert review_rate(Verdict.HOLD_VERIFY) == 1.0
    s1 = sample_for_review(decs, 0.3, seed=42)
    s2 = sample_for_review(decs, 0.3, seed=42)
    assert s1 == s2 and len(s1) == 3
    strat = stratified_sample(decs, per_verdict=2, seed=42)
    assert len(strat) == 4
    assert len(resample(decs, 5, seed=42)) == 5
    assert estimate_error_rate(20, 2) == 0.1
    lo, hi = confidence_interval(0.1, 100)
    assert lo < 0.1 < hi
    assert sample_report(strat)["sample_size"] == 4
    ss = SampleSet(42, s1)
    assert ss.seed == 42
    assert seed_sampler(42).randint(1, 10) == seed_sampler(42).randint(1, 10)
