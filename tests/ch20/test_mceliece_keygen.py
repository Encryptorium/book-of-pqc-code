"""Tests for McEliece key generation."""

import random

from mceliece.mceliece import keygen
from mceliece.gf2 import mat_mul, gf2_mat_inv, identity

M = 4
IRRED = 0b10011
T = 2


def test_keygen_public_key_shape():
    """G_pub is k-by-n."""
    pub, _ = keygen(M, T, IRRED, random.Random(42))
    G_pub = pub["G_pub"]
    assert len(G_pub) == pub["k"]
    assert all(len(row) == pub["n"] for row in G_pub)


def test_keygen_s_invertible():
    """S * S_inv = I_k."""
    _, sec = keygen(M, T, IRRED, random.Random(42))
    S = sec["S"]
    S_inv = sec["S_inv"]
    k = len(S)
    product = mat_mul(S, S_inv)
    Ik = identity(k)
    assert product == Ik


def test_keygen_perm_is_permutation():
    """P has exactly one 1 per row and column."""
    pub, sec = keygen(M, T, IRRED, random.Random(42))
    perm = sec["perm"]
    n = pub["n"]
    assert sorted(perm) == list(range(n))


def test_keygen_perm_inv_consistent():
    """perm_inv is the true inverse of perm."""
    _, sec = keygen(M, T, IRRED, random.Random(42))
    perm = sec["perm"]
    perm_inv = sec["perm_inv"]
    for i, j in enumerate(perm):
        assert perm_inv[j] == i


def test_keygen_multiple_seeds():
    """Key generation succeeds across multiple seeds."""
    for seed in range(10):
        pub, sec = keygen(M, T, IRRED, random.Random(seed))
        assert pub["n"] == 16
        assert pub["k"] == 8
        assert pub["t"] == 2
