"""Tests for HQC key generation."""

import random

from hqc.hqc import keygen
from hqc.poly_gf2 import poly_add, poly_mul, poly_weight


N, W, W_R, W_E, R = 83, 3, 3, 3, 17


def test_keygen_key_shapes():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    assert len(pk["s"]) == N
    assert len(pk["h"]) == N
    assert len(sk["x"]) == N
    assert len(sk["y"]) == N


def test_keygen_sparse_weights():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    assert poly_weight(sk["x"]) == W
    assert poly_weight(sk["y"]) == W


def test_keygen_h_consistency():
    """Verify h = x + s*y."""
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    h_recomputed = poly_add(sk["x"], poly_mul(pk["s"], sk["y"], N))
    assert pk["h"] == h_recomputed


def test_keygen_multiple_seeds():
    for seed in range(20):
        pk, sk = keygen(N, W, W_R, W_E, R, random.Random(seed))
        assert len(pk["h"]) == N
        assert poly_weight(sk["x"]) == W
        assert poly_weight(sk["y"]) == W


def test_keygen_different_keys():
    pk1, _ = keygen(N, W, W_R, W_E, R, random.Random(0))
    pk2, _ = keygen(N, W, W_R, W_E, R, random.Random(1))
    assert pk1["h"] != pk2["h"]
