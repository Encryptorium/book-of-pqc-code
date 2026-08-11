"""Tests for generalized Goppa code construction."""

import random

from mceliece.gf2 import mat_mul, mat_vec_mul, transpose
from mceliece.gf2m import poly_eval, poly_is_irreducible
from mceliece.goppa import goppa_parity_check, find_irreducible_goppa_poly, full_support

M = 4
IRRED = 0b10011
T = 2


def _make_goppa_code(seed=42):
    rng = random.Random(seed)
    support = full_support(M)
    g_coeffs = find_irreducible_goppa_poly(M, IRRED, T, rng)
    support = [a for a in support if poly_eval(g_coeffs, a, M, IRRED) != 0]
    H = goppa_parity_check(M, IRRED, g_coeffs, support)
    return H, g_coeffs, support


def test_goppa_poly_irreducible():
    """The generated Goppa polynomial is irreducible."""
    _, g_coeffs, _ = _make_goppa_code()
    assert poly_is_irreducible(g_coeffs, M, IRRED)


def test_goppa_parity_shape():
    """H has shape (m*t, n) = (8, 16) for full support."""
    H, _, support = _make_goppa_code()
    assert len(H) == M * T
    assert len(H[0]) == len(support)
    assert len(support) == 16  # irreducible g => no roots in GF(16)


def test_goppa_parity_rank():
    """H has full rank m*t = 8."""
    H, _, _ = _make_goppa_code()
    # Gaussian elimination to check rank
    from mceliece.gf2 import gauss_systematic
    H_sys, _ = gauss_systematic(H)
    # if gauss_systematic succeeds, H is full rank
    assert len(H_sys) == M * T


def test_goppa_support_no_roots():
    """No support element is a root of g(x)."""
    _, g_coeffs, support = _make_goppa_code()
    for lj in support:
        assert poly_eval(g_coeffs, lj, M, IRRED) != 0


def test_goppa_multiple_seeds():
    """Construction works across multiple seeds."""
    for seed in range(10):
        H, g_coeffs, support = _make_goppa_code(seed)
        assert len(H) == M * T
        assert all(len(row) == len(support) for row in H)
