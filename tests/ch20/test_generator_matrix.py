"""Tests for generator matrix derivation from parity-check matrix."""

import random

from mceliece.gf2 import mat_mul, transpose, identity, generator_from_parity
from mceliece.gf2m import poly_eval
from mceliece.goppa import goppa_parity_check, find_irreducible_goppa_poly, full_support

M = 4
IRRED = 0b10011
T = 2


def _make_G_and_H(seed=42):
    rng = random.Random(seed)
    support = full_support(M)
    g_coeffs = find_irreducible_goppa_poly(M, IRRED, T, rng)
    support = [a for a in support if poly_eval(g_coeffs, a, M, IRRED) != 0]
    H = goppa_parity_check(M, IRRED, g_coeffs, support)
    G, col_perm = generator_from_parity(H)
    # Reorder H columns to match systematic ordering
    H_sys_order = [[H[r][col_perm[c]] for c in range(len(support))]
                    for r in range(len(H))]
    return G, H_sys_order, col_perm, len(support)


def test_g_dimensions():
    """G is k-by-n where k = n - m*t."""
    G, _, _, n = _make_G_and_H()
    k = n - M * T
    assert len(G) == k
    assert all(len(row) == n for row in G)


def test_g_times_ht_is_zero():
    """G * H^T = 0 over GF(2)."""
    G, H, _, _ = _make_G_and_H()
    Ht = transpose(H)
    GHt = mat_mul(G, Ht)
    for row in GHt:
        for val in row:
            assert val == 0


def test_g_systematic_form():
    """G = [B^T | I_k]: last k columns form an identity."""
    G, _, _, n = _make_G_and_H()
    k = len(G)
    nk = n - k
    for r in range(k):
        for c in range(k):
            expected = 1 if r == c else 0
            assert G[r][nk + c] == expected


def test_g_times_ht_multiple_seeds():
    """G * H^T = 0 for multiple seeds."""
    for seed in range(10):
        G, H, _, _ = _make_G_and_H(seed)
        Ht = transpose(H)
        GHt = mat_mul(G, Ht)
        for row in GHt:
            for val in row:
                assert val == 0, f"G*H^T != 0 for seed {seed}"
