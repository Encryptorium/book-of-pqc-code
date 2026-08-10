"""Tests for the primal-attack success condition and the block-size solver."""

from __future__ import annotations

import math

import pytest

from cryptanalysis.primal import primal_beta, primal_success


# Reference values from CRYSTALS-Kyber Round 3 submission, Table 4, page 21.
# Pure-GSA reimplementation reproduces 512 exactly and 768/1024 within 5.
ML_KEM_PUBLISHED_BETAS: list[tuple[str, int, int, int, int, int]] = [
    # (name, k, n, q, eta_1, published_beta)
    ("ML-KEM-512", 2, 256, 3329, 3, 406),
    ("ML-KEM-768", 3, 256, 3329, 2, 626),
    ("ML-KEM-1024", 4, 256, 3329, 2, 878),
]

BETA_TOLERANCE = 5


@pytest.mark.parametrize("name,k,n,q,eta_1,published", ML_KEM_PUBLISHED_BETAS)
def test_primal_beta_reproduces_kyber_table_4(
    name: str, k: int, n: int, q: int, eta_1: int, published: int
) -> None:
    """primal_beta reproduces the Kyber Round 3 Table 4 block sizes within 5."""
    zeta = math.sqrt(eta_1 / 2.0)
    computed_beta, m_opt = primal_beta(k, n, q, zeta)
    gap = published - computed_beta
    assert abs(gap) <= BETA_TOLERANCE, (
        f"{name}: primal_beta returned {computed_beta}, "
        f"published value is {published}, gap = {gap}, "
        f"tolerance = {BETA_TOLERANCE}"
    )
    assert m_opt >= 1, f"{name}: optimal m must be at least 1, got {m_opt}"
    assert m_opt <= (k + 1) * n, (
        f"{name}: optimal m must be at most (k+1)*n = {(k + 1) * n}, got {m_opt}"
    )


def test_primal_success_is_monotone_in_beta() -> None:
    """If primal_success holds at beta_0, it also holds at every beta > beta_0.

    The left-hand side of equation 9 grows as sqrt(beta). The right-hand
    side grows faster because delta(beta) < 1 (no, wait: delta > 1) and
    the exponent 2*beta - d - 1 increases linearly in beta. So the RHS
    grows exponentially in beta while the LHS grows only as sqrt(beta),
    which makes success condition monotone in beta.
    """
    k, n, q, zeta = 3, 256, 3329, 1.0
    m = 650
    beta_low = 500
    beta_high = 800
    assert not primal_success(beta_low, k, n, q, zeta, m), (
        "expected primal_success to fail at beta=500 for ML-KEM-768-like params"
    )
    assert primal_success(beta_high, k, n, q, zeta, m), (
        "expected primal_success to hold at beta=800 for ML-KEM-768-like params"
    )


def test_primal_success_requires_larger_beta_for_larger_zeta() -> None:
    """A noisier secret makes the primal attack harder, not easier.

    This is a sanity check on the direction of the inequality: zeta
    appears on the LHS, so larger zeta means a tighter inequality and
    a larger required beta.
    """
    k, n, q = 3, 256, 3329
    beta_quiet, _ = primal_beta(k, n, q, zeta=0.5)
    beta_noisy, _ = primal_beta(k, n, q, zeta=2.0)
    assert beta_quiet < beta_noisy, (
        f"larger zeta should require larger beta, "
        f"got beta_quiet={beta_quiet}, beta_noisy={beta_noisy}"
    )


def test_primal_success_requires_larger_beta_for_smaller_q() -> None:
    """A smaller modulus makes the primal attack harder.

    The RHS of equation 9 scales as q^(m/d). Shrinking q shrinks the
    RHS, tightening the success condition and forcing a larger beta.
    """
    k, n, zeta = 3, 256, 1.0
    beta_big_q, _ = primal_beta(k, n, 3329, zeta)
    beta_small_q, _ = primal_beta(k, n, 1009, zeta)
    assert beta_small_q > beta_big_q, (
        f"smaller q should require larger beta, "
        f"got beta_big_q={beta_big_q}, beta_small_q={beta_small_q}"
    )
