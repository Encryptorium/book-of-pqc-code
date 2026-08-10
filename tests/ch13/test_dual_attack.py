"""Tests for the dual-distinguisher advantage bound.

The bound is the CRYSTALS-Kyber Round 3 submission Section 5.1.3
expression :math:`\\varepsilon = 4 \\exp(-2 \\pi^2 \\tau^2)` with
:math:`\\tau = \\|\\mathbf{w}\\| \\sigma / q`. It is a bound on the
maximal variation distance, not a probability: for a very short dual
vector it exceeds 1, in which range it is capped at 1 in
interpretation and no longer a meaningful quantitative estimate.
"""

from __future__ import annotations

import math

from cryptanalysis.dual import dual_advantage


def test_dual_advantage_saturates_above_one_for_short_w() -> None:
    """A very short dual vector pushes the raw bound above 1 (capped in interpretation)."""
    # If w_norm * sigma / q is tiny, 4 * exp(-2 pi^2 * tiny^2) -> 4.
    assert dual_advantage(w_norm=0.01, sigma=1.0, q=3329) > 1.0


def test_dual_advantage_decays_toward_zero_for_long_w() -> None:
    """A long dual vector gives a negligible distinguishing bound."""
    # At w_norm * sigma / q = 2, 4 * exp(-2 pi^2 * 4) ~ 2e-34, which is
    # effectively zero.
    advantage = dual_advantage(w_norm=2.0 * 3329, sigma=1.0, q=3329)
    assert advantage < 1e-5


def test_dual_advantage_monotonic_in_w_norm() -> None:
    """Finding a shorter dual vector always improves the bound."""
    sigma = 1.0
    q = 3329
    norms = [100.0, 500.0, 1000.0, 2000.0, 3000.0]
    advantages = [dual_advantage(w, sigma, q) for w in norms]
    assert all(advantages[i] > advantages[i + 1] for i in range(len(advantages) - 1))


def test_dual_advantage_monotonic_in_sigma() -> None:
    """A noisier LWE instance is harder to distinguish from uniform."""
    w_norm = 500.0
    q = 3329
    sigmas = [0.5, 1.0, 1.5, 2.0, 3.0]
    advantages = [dual_advantage(w_norm, s, q) for s in sigmas]
    assert all(advantages[i] > advantages[i + 1] for i in range(len(advantages) - 1))


def test_dual_advantage_closed_form_at_unit_ratio() -> None:
    """At w_norm * sigma / q = 1, the bound = 4 * exp(-2 pi^2) ~ 1.07e-8."""
    advantage = dual_advantage(w_norm=3329.0, sigma=1.0, q=3329)
    assert abs(advantage - 4.0 * math.exp(-2.0 * math.pi**2)) < 1e-15
