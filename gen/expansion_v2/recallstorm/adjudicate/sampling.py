"""Deterministic sampling of SKU decisions for QA review."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import random

from contract import SkuDecision, Verdict


@dataclass
class SampleSet:
    """Sampled subset of SkuDecisions with seed metadata."""

    seed: int
    items: list[SkuDecision] = field(default_factory=list)


def seed_sampler(seed: int = 42) -> random.Random:
    """Return a deterministic Random instance seeded with seed."""
    return random.Random(int(seed))


def review_rate(verdict: Verdict) -> float:
    """Return default QA sampling rate for a Verdict."""
    if verdict == Verdict.HOLD_VERIFY:
        return 1.0
    if verdict == Verdict.PULL:
        return 0.25
    return 0.05


def sample_for_review(decisions: list[SkuDecision], rate: float = 0.1, seed: int = 42) -> list[SkuDecision]:
    """Deterministically sample a fraction of decisions for QA review."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError("rate must be in [0.0, 1.0]")
    if not decisions or rate == 0.0:
        return []
    rng = seed_sampler(seed)
    k = max(1, int(round(len(decisions) * rate)))
    ordered = sorted(decisions, key=lambda d: d.sku_id)
    return rng.sample(ordered, min(k, len(ordered)))


def stratified_sample(decisions: list[SkuDecision], per_verdict: int = 2, seed: int = 42) -> list[SkuDecision]:
    """Deterministically sample up to per_verdict items from each Verdict bucket."""
    if per_verdict < 0:
        raise ValueError("per_verdict must be non-negative")
    rng = seed_sampler(seed)
    out: list[SkuDecision] = []
    for v in (Verdict.PULL, Verdict.HOLD_VERIFY, Verdict.KEEP):
        bucket = sorted([d for d in decisions if d.verdict == v], key=lambda x: x.sku_id)
        if bucket and per_verdict > 0:
            out.extend(rng.sample(bucket, min(per_verdict, len(bucket))))
    return out


def resample(decisions: list[SkuDecision], n: int, seed: int = 42) -> list[SkuDecision]:
    """Draw n decisions without replacement (clamped to len(decisions))."""
    if n <= 0 or not decisions:
        return []
    rng = seed_sampler(seed)
    ordered = sorted(decisions, key=lambda d: d.sku_id)
    return rng.sample(ordered, min(n, len(ordered)))


def estimate_error_rate(total_reviewed: int, errors_found: int) -> float:
    """Compute empirical error rate in [0.0, 1.0]."""
    if total_reviewed <= 0:
        return 0.0
    if errors_found < 0 or errors_found > total_reviewed:
        raise ValueError("Invalid errors_found count")
    return round(errors_found / total_reviewed, 4)


def confidence_interval(rate: float, n: int) -> tuple[float, float]:
    """Compute 95% normal-approximation confidence interval around rate."""
    if n <= 0:
        return (0.0, 1.0)
    se = math.sqrt(max(0.0, rate * (1.0 - rate)) / n)
    lo = max(0.0, round(rate - 1.96 * se, 4))
    hi = min(1.0, round(rate + 1.96 * se, 4))
    return (lo, hi)


def sample_report(sample: list[SkuDecision]) -> dict:
    """Summarize a sampled list of SkuDecisions."""
    return {
        "sample_size": len(sample),
        "by_verdict": {
            v.value: sum(1 for d in sample if d.verdict == v)
            for v in (Verdict.PULL, Verdict.HOLD_VERIFY, Verdict.KEEP)
        },
    }
