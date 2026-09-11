"""Tests for the core-SVP cost exponents and root-Hermite-factor."""

from __future__ import annotations

import math

from cryptanalysis.core_svp import (
    CLASSICAL_SIEVE_EXPONENT,
    QUANTUM_SIEVE_EXPONENT,
    classical_bits,
    delta_beta,
    quantum_bits,
)


def test_sieving_exponents_match_bdgl_and_laarhoven() -> None:
    """Classical 0.292 from BDGL 2016, quantum 0.265 from Laarhoven."""
    assert CLASSICAL_SIEVE_EXPONENT == 0.292
    assert QUANTUM_SIEVE_EXPONENT == 0.265
    assert QUANTUM_SIEVE_EXPONENT < CLASSICAL_SIEVE_EXPONENT


def test_classical_bits_closed_form() -> None:
    """classical_bits(beta) == 0.292 * beta for every beta."""
    for beta in (50, 100, 200, 400, 600, 800, 1000):
        assert classical_bits(beta) == 0.292 * beta


def test_quantum_bits_closed_form() -> None:
    """quantum_bits(beta) == 0.265 * beta for every beta."""
    for beta in (50, 100, 200, 400, 600, 800, 1000):
        assert quantum_bits(beta) == 0.265 * beta


def test_classical_bits_strictly_monotonic() -> None:
    """The classical cost is strictly increasing in beta."""
    betas = list(range(50, 1001, 25))
    values = [classical_bits(b) for b in betas]
    assert all(values[i] < values[i + 1] for i in range(len(values) - 1))


def test_quantum_bits_strictly_monotonic() -> None:
    """The quantum cost is strictly increasing in beta."""
    betas = list(range(50, 1001, 25))
    values = [quantum_bits(b) for b in betas]
    assert all(values[i] < values[i + 1] for i in range(len(values) - 1))


def test_delta_beta_matches_bkz_2_headline_value() -> None:
    """At beta = 100, the Chen-Nguyen 2011 BKZ 2.0 paper reports
    delta ~ 1.0094. Our closed-form matches to within 0.0002.
    """
    computed = delta_beta(100)
    assert abs(computed - 1.0094) < 0.0002, (
        f"delta_beta(100) = {computed:.5f}, expected ~1.0094 from BKZ 2.0"
    )


def test_delta_beta_regression_anchors() -> None:
    """Regression test: the formula's output at a handful of block
    sizes used throughout Chapter 13. Values are from the Chen 2013
    formula implemented in core_svp.py and serve as fixed-point
    anchors for the chapter's tables.
    """
    anchors = {
        60: 1.011453,
        100: 1.009259,
        200: 1.006283,
        500: 1.003404,
        1000: 1.002043,
    }
    for beta, expected in anchors.items():
        computed = delta_beta(beta)
        assert abs(computed - expected) < 1e-5, (
            f"delta_beta({beta}) drifted: computed={computed:.6f}, "
            f"anchor={expected:.6f}"
        )


def test_delta_beta_strictly_decreasing() -> None:
    """delta(beta) decreases across beta in [50, 1000]: more block size,
    shorter output.

    The range is part of the claim. The asymptotic formula is not
    decreasing over its whole accepted domain, and Chapter 13 says it is
    unsuitable at small beta: delta_beta(2) returns 0.54, and the values
    rise rather than fall until beta is around 12.
    """
    betas = list(range(50, 1001, 25))
    values = [delta_beta(b) for b in betas]
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1))


def test_delta_beta_asymptotes_above_one() -> None:
    """delta(beta) exceeds 1 across the sampled beta range.

    Not because of any geometric lower bound: a reduced vector CAN be
    shorter than det(L)^(1/d). The basis diag(1, 100) has lambda_1 = 1
    against a determinant scale of 10. The root-Hermite factor is a model
    of reduction quality normalized by that determinant scale, and what
    is checked here is that the model stays above 1 where it is used.
    Below beta about 12 it does not, which is why the samples start at 50.
    """
    for beta in (50, 100, 250, 500, 1000):
        assert delta_beta(beta) > 1.0


def test_classical_cost_at_ml_kem_768_matches_published() -> None:
    """At beta = 626 (Kyber Round 3 Table 4 for Kyber768), the toy's
    floored classical cost is 182 against the published 183.

    The comparison is stated and the gap is not explained away. This
    estimator floors 0.292 * 626 = 182.8 to 182; the submission's Table 4
    reports 183. Kyber Round 3 Section 5.1.1 gives the sqrt(3/2)
    asymptotic base and the rounded 0.292 model, and it does not publish
    the arithmetic that produced the table entry, so no account of how
    the authors got there is asserted here. For reference the unrounded
    exponent is log2(sqrt(3/2)) = 0.292481, and one bit is the tolerance
    this comparison is read at.
    """
    assert math.floor(classical_bits(626)) == 182
    assert abs(math.floor(classical_bits(626)) - 183) <= 1
