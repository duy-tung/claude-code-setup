#!/usr/bin/env python3
"""
Small, dependency-free statistics helpers for paired A/B eval.

All stdlib. Used to turn noisy, stochastic agent runs into a defensible
"did B beat A" signal:
  - solve_rate / pass_hat_k        : reliability summaries
  - mcnemar_exact                  : significance of a paired pass/fail diff
  - bootstrap_diff_ci              : CI on the paired solve-rate improvement
"""
from __future__ import annotations

import math
import random


def solve_rate(solved: list[bool]) -> float:
    return sum(1 for s in solved if s) / len(solved) if solved else 0.0


def pass_hat_k(solved: list[bool]) -> float:
    """pass^k empirical estimate: 1.0 only if EVERY run solved (reliability)."""
    return 1.0 if solved and all(solved) else 0.0


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value on discordant pairs.

    b = #pairs where A solved & B failed; c = #pairs where A failed & B solved.
    Tests H0: the two configs are equally likely to flip an outcome.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def sign_test(diffs: list[float]) -> tuple[int, int, float]:
    """Two-sided exact sign test on paired differences.

    Returns (n_below_zero, n_above_zero, p). Chosen over a mean comparison for
    the efficiency metrics because a single runaway run — one task answering at
    ten times its usual length — moves a mean and does not move a count.

    Ties are dropped, the standard treatment, which keeps the test honest when a
    metric comes out identical in both arms.
    """
    below = sum(1 for d in diffs if d < 0)
    above = sum(1 for d in diffs if d > 0)
    n = below + above
    if n == 0:
        return (0, 0, 1.0)
    k = min(below, above)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return (below, above, min(1.0, 2 * tail))


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2


def bootstrap_diff_ci(diffs: list[int], iters: int = 10000,
                      alpha: float = 0.05, seed: int = 0) -> tuple[float, float, float]:
    """Bootstrap CI on the mean paired difference (B_solved - A_solved per pair).

    Returns (point_estimate, lo, hi) — the improvement in solve rate and its CI.
    """
    if not diffs:
        return (0.0, 0.0, 0.0)
    rng = random.Random(seed)
    n = len(diffs)
    means = []
    for _ in range(iters):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo = means[int((alpha / 2) * iters)]
    hi = means[min(iters - 1, int((1 - alpha / 2) * iters))]
    return (sum(diffs) / n, lo, hi)
