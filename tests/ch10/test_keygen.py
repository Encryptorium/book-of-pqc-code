"""Tests for the Regev keygen routine."""

import numpy as np

from regev_pke import keygen


def test_keygen_shapes_and_dtypes(toy):
    rng = np.random.default_rng(seed=0)
    (A, b), s = keygen(toy, rng)
    assert A.shape == (toy.m, toy.n)
    assert b.shape == (toy.m,)
    assert s.shape == (toy.n,)
    assert A.dtype == np.int64
    assert b.dtype == np.int64
    assert s.dtype == np.int64


def test_keygen_values_in_canonical_range(toy):
    rng = np.random.default_rng(seed=1)
    (A, b), s = keygen(toy, rng)
    assert np.all(A >= 0) and np.all(A < toy.q)
    assert np.all(b >= 0) and np.all(b < toy.q)
    assert np.all(s >= 0) and np.all(s < toy.q)


def test_keygen_satisfies_lwe_equation(toy):
    rng = np.random.default_rng(seed=2)
    (A, b), s = keygen(toy, rng)
    # Recompute A @ s via an explicit Python-level integer loop so this
    # test's verification path is independent of numpy's matmul operator
    # used inside keygen. A bug in numpy matmul would corrupt both paths
    # in the same direction and hide the error otherwise.
    As_loop = np.array(
        [
            sum(int(A[i, j]) * int(s[j]) for j in range(toy.n)) % toy.q
            for i in range(toy.m)
        ],
        dtype=np.int64,
    )
    residual = (b - As_loop) % toy.q
    # Map residuals into symmetric representatives and confirm |e| <= B.
    half_q = toy.q // 2
    as_signed = np.where(residual > half_q, residual - toy.q, residual)
    assert np.all(np.abs(as_signed) <= toy.noise_bound)


def test_keygen_reproducible_under_fixed_seed(toy):
    rng1 = np.random.default_rng(seed=42)
    (A1, b1), s1 = keygen(toy, rng1)
    rng2 = np.random.default_rng(seed=42)
    (A2, b2), s2 = keygen(toy, rng2)
    assert np.array_equal(A1, A2)
    assert np.array_equal(b1, b2)
    assert np.array_equal(s1, s2)
