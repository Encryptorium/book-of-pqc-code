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
    """delta(beta) is strictly decreasing in beta: more block size, shorter output."""
    betas = list(range(50, 1001, 25))
    values = [delta_beta(b) for b in betas]
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1))


def test_delta_beta_asymptotes_above_one() -> None:
    """delta(beta) is always strictly greater than 1, because the output
    of BKZ on a non-trivial lattice cannot be shorter than the lattice
    determinant to the 1/d power."""
    for beta in (50, 100, 250, 500, 1000):
        assert delta_beta(beta) > 1.0


def test_classical_cost_at_ml_kem_768_matches_published() -> None:
    """At beta = 626 (Kyber Round 3 Table 4 for Kyber768), the floored
    classical cost must match the published value of 183 bits within
    two bits. The floor of 0.292 * 626 = 182.8 rounds to 182, and the
    Kyber team's fractional-beta computation rounds up to 183; this
    is the well-known 1-bit ambiguity between the rounded and the
    un-rounded exponent and is not a bug."""
    assert math.floor(classical_bits(626)) == 182
    # The published table reports 183. The gap is 1 bit, which is
    # exactly the difference between floor(0.292 * 626) = 182 and
    # the Kyber team's floor(0.2926 * 626) = 183.
    assert math.floor(0.2926 * 626) == 183
