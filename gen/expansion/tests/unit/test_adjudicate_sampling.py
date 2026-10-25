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


def test_sampling_and_ci():
    decs = [
        SkuDecision(f"S{i}", Verdict.PULL if i % 2 == 0 else Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "r")
        for i in range(10)
    ]
    s1 = sample_for_review(decs, 4, seed=99)
    s2 = sample_for_review(decs, 4, seed=99)
    assert s1 == s2
    strat = stratified_sample(decs, 2, seed=99)
    assert len(strat) == 4
    boot = resample(s1, 3, seed=10)
    assert len(boot) == 3
    ss = SampleSet(99, tuple(s1))
    assert len(ss.items) == 4
    assert review_rate(5, 10) == 0.5
    assert estimate_error_rate(1, 10) == 0.1
    lo, hi = confidence_interval(1, 10)
    assert 0.0 <= lo <= 0.1 <= hi <= 1.0
    rep = sample_report(s1, 0)
    assert rep["sample_size"] == 4
    assert seed_sampler(1).randint(1, 100) == seed_sampler(1).randint(1, 100)
