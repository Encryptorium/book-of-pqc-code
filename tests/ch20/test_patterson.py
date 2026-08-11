"""Tests for Patterson's decoding algorithm."""

import random
from itertools import combinations

from mceliece.gf2 import vec_add, weight, generator_from_parity
from mceliece.gf2m import poly_eval
from mceliece.goppa import goppa_parity_check, find_irreducible_goppa_poly, full_support
from mceliece.patterson import patterson_decode

M = 4
IRRED = 0b10011
T = 2


def _setup(seed=42):
    rng = random.Random(seed)
    support = full_support(M)
    g_coeffs = find_irreducible_goppa_poly(M, IRRED, T, rng)
    support = [a for a in support if poly_eval(g_coeffs, a, M, IRRED) != 0]
    H = goppa_parity_check(M, IRRED, g_coeffs, support)
    G, col_perm = generator_from_parity(H)
    # Reorder support to match systematic column ordering
    support_sys = [support[col_perm[i]] for i in range(len(support))]
    return G, g_coeffs, support_sys


def _encode(msg, G):
    n = len(G[0])
    c = [0] * n
    for i, mi in enumerate(msg):
        if mi:
            c = vec_add(c, G[i])
    return c


def test_patterson_no_error():
    """A valid codeword with no errors passes through unchanged."""
    G, g_coeffs, support = _setup()
    msg = [1, 0, 1, 1, 0, 0, 1, 0]
    codeword = _encode(msg, G)
    decoded = patterson_decode(codeword, g_coeffs, support, M, IRRED)
    assert decoded == codeword


def test_patterson_single_error():
    """Patterson corrects a single-bit error at every position."""
    G, g_coeffs, support = _setup()
    n = len(support)
    msg = [1, 1, 0, 1, 0, 1, 0, 0]
    codeword = _encode(msg, G)
    for pos in range(n):
        received = list(codeword)
        received[pos] ^= 1
        decoded = patterson_decode(received, g_coeffs, support, M, IRRED)
        assert decoded == codeword, f"failed at error position {pos}"


def test_patterson_double_error_exhaustive():
    """Patterson corrects all C(16,2) = 120 weight-2 error patterns."""
    G, g_coeffs, support = _setup()
    n = len(support)
    msg = [0, 1, 1, 0, 1, 0, 1, 1]
    codeword = _encode(msg, G)
    for i, j in combinations(range(n), 2):
        received = list(codeword)
        received[i] ^= 1
        received[j] ^= 1
        decoded = patterson_decode(received, g_coeffs, support, M, IRRED)
        assert decoded == codeword, f"failed at error positions ({i}, {j})"


def test_patterson_multiple_seeds():
    """Patterson decodes correctly across multiple key seeds."""
    for seed in range(5):
        G, g_coeffs, support = _setup(seed)
        msg = [1, 0, 0, 1, 1, 0, 1, 0]
        codeword = _encode(msg, G)
        # weight-2 error at positions 0 and 5
        received = list(codeword)
        received[0] ^= 1
        received[5] ^= 1
        decoded = patterson_decode(received, g_coeffs, support, M, IRRED)
        assert decoded == codeword, f"failed for seed {seed}"
