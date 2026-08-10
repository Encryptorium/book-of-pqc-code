"""FORS few-time analysis: coverage, its approximation, and reuse thresholds.

FORS forgery does not invert a hash. An adversary who has seen `q` signatures on
one FORS instance holds the secrets for whichever leaf indices those signatures
revealed, and forges as soon as a candidate digest selects only indices already
covered. A single index in one tree survives all `q` signatures with probability
`(1 - 1/t)**q`, so it is covered with probability `1 - (1 - 1/t)**q`, and all `k`
trees are covered with the `k`-th power of that.

The literature quotes `(q/t)**k`, which is the first-order expansion and holds
only while `q << t`. Both forms are here because the gap between them is the
chapter's point: at the `f` parameter sets `t` falls to 64, the regime where the
approximation stops being an approximation and starts being wrong. It exceeds 1
at `q >= t`, which is not a probability.

Every `q` in this module counts signatures on **one fixed FORS instance**, not
signatures under the key. SLH-DSA spreads signatures across at least `2**63`
positions and permits `2**64` per key, so the two differ by the position
distribution `expected_position_collisions` models. Reading a threshold here as
a key lifetime is the misreading the distinction guards against.

Standard library only.
"""

from __future__ import annotations

import math


def single_signature_log2_forgery(k: int, a: int) -> int:
    """`log2` of the forgery probability from one signature: `-a * k`.

    At `q = 1` the adversary holds exactly one index per tree, so a fresh digest
    matches with probability `(1/t)**k = 2**(-ak)`. Exact and integral, which is
    why it is the one figure in this module that is not a float.
    """
    return -a * k


def log2_fors_forgery(q: int, k: int, t: int) -> float:
    """`log2` of the exact coverage probability `(1 - (1 - 1/t)**q)**k`.

    Computed through `log1p` and `expm1` rather than by raising `1 - 1/t` to the
    `q`. At the parameter sets in play `1/t` is as small as `2**-14` and `q` runs
    into the thousands, so the naive form loses the whole result to rounding:
    `log1p` keeps the precision in `ln(1 - 1/t)` and `expm1` recovers the
    coverage without ever forming `1 - (a number very close to 1)`.

    Returns `-inf` at `q = 0`, where nothing is covered.
    """
    if q == 0:
        return float("-inf")
    log_miss = q * math.log1p(-1.0 / t)
    covered = -math.expm1(log_miss)
    return k * math.log2(covered)


def log2_fors_forgery_approx(q: int, k: int, t: int) -> float:
    """`log2` of the quoted approximation `(q / t)**k`, valid only for `q << t`.

    The approximation drops every term beyond the first in the expansion of
    `1 - (1 - 1/t)**q`, which is `q/t` to first order. Bernoulli's inequality
    gives `(1 - 1/t)**q >= 1 - q/t`, so the true coverage never exceeds `q/t`
    and this form is an upper bound on the exact one at every `q`: it credits
    the adversary with more than they have.

    Erring in that direction is safe until it stops being a probability, and it
    does that without warning. At `q = t` the bound returns zero bits, meaning
    probability one. Above `t` it returns a positive number, meaning a
    probability greater than one. Nothing in the expression signals that the
    domain has been left, which is why the chapter prints the exact form and
    this one exists only for the comparison.

    Returns `-inf` at `q = 0`, matching `log2_fors_forgery`.
    """
    if q == 0:
        return float("-inf")
    return k * (math.log2(q) - math.log2(t))


def first_q_at_or_above(k: int, t: int, threshold_bits: int) -> int:
    """Smallest `q` whose exact forgery probability reaches `2**-threshold_bits`.

    Doubles `hi` until the threshold is crossed, then bisects. Coverage is
    monotone in `q`, which is what makes the bisection valid; the loop invariant
    is that `lo` is always strictly below the threshold and `hi` always at or
    above it, so `hi` is the answer when they become adjacent.
    """
    lo, hi = 0, 1
    while log2_fors_forgery(hi, k, t) < -threshold_bits:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if log2_fors_forgery(mid, k, t) < -threshold_bits:
            lo = mid
        else:
            hi = mid
    return hi


def expected_position_collisions(q: int, h: int) -> float:
    """Expected FORS instances signed twice, after `q` signatures under one key.

    A birthday count over `2**h` hypertree positions: each of the `q * (q - 1) / 2`
    unordered pairs of signatures lands on the same position with probability
    `2**-h`, and expectation is linear, so no independence assumption is needed
    for the count itself.

    The chapter quotes this as `q**2 / 2**64` at `h = 63`, which is the same
    figure with the pair count rounded up from `q * (q - 1) / 2` to `q**2 / 2`.
    The two agree to within a factor of `1 - 1/q`, so they are indistinguishable
    at the scale that matters and the exact form is used here anyway, because the
    approximation is free to state and costs nothing to avoid.
    """
    return (q * (q - 1) // 2) / 2**h
