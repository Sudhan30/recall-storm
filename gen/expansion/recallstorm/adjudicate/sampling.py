"""Deterministic QA sampling and Wilson/normal confidence intervals for decision audits."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from contract import SkuDecision, Verdict


@dataclass(frozen=True)
class SampleSet:
    """Sampled subset of SkuDecisions for QA review."""

    seed: int
    items: tuple[SkuDecision, ...]


def seed_sampler(seed: int = 42) -> random.Random:
    """Return a deterministic Random instance seeded with seed."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    return random.Random(seed)


def sample_for_review(decisions: list[SkuDecision], n: int = 10, seed: int = 42) -> list[SkuDecision]:
    """Deterministically sample up to n decisions for human QA review."""
    if n < 0:
        raise ValueError("n must be non-negative")
    ordered = sorted(decisions, key=lambda d: d.sku_id)
    rng = seed_sampler(seed)
    return rng.sample(ordered, min(n, len(ordered)))


def stratified_sample(decisions: list[SkuDecision], per_verdict: int = 5, seed: int = 42) -> list[SkuDecision]:
    """Sample up to per_verdict decisions from each Verdict stratum."""
    if per_verdict < 0:
        raise ValueError("per_verdict must be non-negative")
    out: list[SkuDecision] = []
    for idx, v in enumerate((Verdict.PULL, Verdict.HOLD_VERIFY, Verdict.KEEP)):
        group = [d for d in decisions if d.verdict == v]
        out.extend(sample_for_review(group, per_verdict, seed + idx))
    return out


def resample(sample: list[SkuDecision], n: int, seed: int = 42) -> list[SkuDecision]:
    """Bootstrap resample n items with replacement using a fixed seed."""
    if not sample or n <= 0:
        return []
    rng = seed_sampler(seed)
    return [rng.choice(sample) for _ in range(n)]


def review_rate(reviewed: int, total: int) -> float:
    """Compute fraction of total items reviewed."""
    if total <= 0 or reviewed < 0:
        raise ValueError("Invalid reviewed or total counts")
    return min(1.0, reviewed / total)


def estimate_error_rate(errors: int, sample_size: int) -> float:
    """Compute observed error rate in a QA sample."""
    if sample_size <= 0 or errors < 0 or errors > sample_size:
        raise ValueError("Invalid errors or sample_size")
    return errors / sample_size


def confidence_interval(errors: int, sample_size: int, z: float = 1.96) -> tuple[float, float]:
    """Compute Wilson score confidence interval (low, high) for binomial error rate."""
    p = estimate_error_rate(errors, sample_size)
    n = float(sample_size)
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denom
    return round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)


def sample_report(sample: list[SkuDecision], errors: int = 0) -> dict:
    """Return a QA summary dictionary for a sample."""
    n = len(sample)
    rate = estimate_error_rate(errors, n) if n > 0 else 0.0
    ci = confidence_interval(errors, n) if n > 0 else (0.0, 0.0)
    return {"sample_size": n, "errors": errors, "error_rate": rate, "ci_95": list(ci)}
