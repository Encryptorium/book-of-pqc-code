"""Tests for Ring-LWE and Module-LWE sampling routines."""

import numpy as np

from ring_lwe import (
    RingParams,
    ModuleParams,
    ring_mul_naive,
    sample_ring_secret,
    sample_ring_error,
    sample_ring_uniform,
    sample_ring_lwe,
    sample_module_lwe,
)


def test_sample_ring_secret_shape_and_range() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    s = sample_ring_secret(params, rng)
    assert s.shape == (4,)
    assert s.dtype == np.int64
    assert (s >= 0).all() and (s < 17).all()


def test_sample_ring_error_is_short_in_symmetric_representatives() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    for _ in range(20):
        e = sample_ring_error(params, rng)
        # Each coefficient, lifted to symmetric representatives in
        # [-q/2, q/2), must lie in {-1, 0, 1}.
        sym = np.where(e > 17 // 2, e.astype(np.int64) - 17, e.astype(np.int64))
        assert (np.abs(sym) <= 1).all()


def test_sample_ring_uniform_covers_range() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    u = sample_ring_uniform(params, rng)
    assert u.shape == (4,)
    assert (u >= 0).all() and (u < 17).all()


def test_sample_ring_lwe_satisfies_defining_identity() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    for _ in range(20):
        a, s, e, b = sample_ring_lwe(params, rng)
        expected = (ring_mul_naive(a, s, 17) + e) % 17
        np.testing.assert_array_equal(b, expected)


def test_sample_ring_lwe_shapes() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    a, s, e, b = sample_ring_lwe(params, rng)
    for arr in (a, s, e, b):
        assert arr.shape == (4,)
        assert arr.dtype == np.int64


def test_sample_module_lwe_shapes() -> None:
    params = ModuleParams(n=4, q=17, k=2, m=3, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    assert A.shape == (3, 2, 4)
    assert s.shape == (2, 4)
    assert e.shape == (3, 4)
    assert b.shape == (3, 4)


def test_sample_module_lwe_satisfies_defining_identity() -> None:
    params = ModuleParams(n=4, q=17, k=2, m=3, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    for i in range(params.m):
        row = np.zeros(params.n, dtype=np.int64)
        for j in range(params.k):
            row = (row + ring_mul_naive(A[i, j], s[j], params.q)) % params.q
        expected = (row + e[i]) % params.q
        np.testing.assert_array_equal(b[i], expected)


def test_sample_ring_lwe_at_larger_toy_ring() -> None:
    # Smoke test at (n, q) = (16, 97). Here 2n = 32 and q - 1 = 96,
    # and 32 divides 96, so the full negacyclic NTT is available.
    params = RingParams(n=16, q=97, m=1, noise_bound=3)
    assert params.ntt_available() is True
    rng = np.random.default_rng(seed=0)
    a, s, e, b = sample_ring_lwe(params, rng)
    assert a.shape == s.shape == e.shape == b.shape == (16,)
    expected = (ring_mul_naive(a, s, 97) + e) % 97
    np.testing.assert_array_equal(b, expected)


def test_sample_ring_lwe_at_ml_kem_ring_uses_naive_multiplication() -> None:
    # The ML-KEM ring (n = 256, q = 3329) does not admit the full
    # negacyclic NTT, but the ring itself is well-defined and
    # sample_ring_lwe uses the schoolbook ring_mul_naive under the
    # hood, so sampling still works. Ch 11 will replace the naive
    # multiplication with ML-KEM's partial NTT.
    params = RingParams(n=256, q=3329, m=1, noise_bound=2)
    assert params.ntt_available() is False
    rng = np.random.default_rng(seed=0)
    a, s, e, b = sample_ring_lwe(params, rng)
    assert a.shape == s.shape == e.shape == b.shape == (256,)
    expected = (ring_mul_naive(a, s, 3329) + e) % 3329
    np.testing.assert_array_equal(b, expected)
