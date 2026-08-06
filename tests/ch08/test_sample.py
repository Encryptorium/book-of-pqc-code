"""Tests for the LWE sampling routines."""

import numpy as np

from lwe import (
    sample_secret,
    sample_error,
    sample_lwe,
    sample_uniform,
)


def test_sample_secret_shape_and_range(toy):
    rng = np.random.default_rng(seed=0)
    s = sample_secret(toy, rng)
    assert s.shape == (toy.n,)
    assert s.dtype == np.int64
    assert np.all(s >= 0)
    assert np.all(s < toy.q)


def test_sample_error_shape_and_small_entries(toy):
    rng = np.random.default_rng(seed=1)
    e = sample_error(toy, rng)
    assert e.shape == (toy.m,)
    assert e.dtype == np.int64
    # Error entries are drawn from {-1, 0, 1} and reduced mod 97;
    # so each entry is in {0, 1, 96}.
    allowed = {0, 1, 96}
    assert set(int(x) for x in e).issubset(allowed)


def test_sample_lwe_shapes_and_equation(toy):
    rng = np.random.default_rng(seed=2)
    s = sample_secret(toy, rng)
    A, b = sample_lwe(toy, s, rng)
    assert A.shape == (toy.m, toy.n)
    assert b.shape == (toy.m,)
    assert A.dtype == np.int64
    assert b.dtype == np.int64
    assert np.all(A >= 0) and np.all(A < toy.q)
    assert np.all(b >= 0) and np.all(b < toy.q)
    # b - A @ s must be a small error in symmetric representatives.
    residual = (b - A @ s) % toy.q
    # Map residuals into {-1, 0, 1} ∪ {q-1 == -1 mod q}.
    as_signed = np.where(residual > toy.q // 2, residual - toy.q, residual)
    assert np.all(np.abs(as_signed) <= toy.noise_bound)


def test_sample_uniform_shapes_and_range(toy):
    rng = np.random.default_rng(seed=3)
    A, u = sample_uniform(toy, rng)
    assert A.shape == (toy.m, toy.n)
    assert u.shape == (toy.m,)
    assert np.all(u >= 0) and np.all(u < toy.q)


def test_sample_lwe_reproducible_under_fixed_seed(toy):
    rng1 = np.random.default_rng(seed=42)
    s1 = sample_secret(toy, rng1)
    A1, b1 = sample_lwe(toy, s1, rng1)

    rng2 = np.random.default_rng(seed=42)
    s2 = sample_secret(toy, rng2)
    A2, b2 = sample_lwe(toy, s2, rng2)

    assert np.array_equal(s1, s2)
    assert np.array_equal(A1, A2)
    assert np.array_equal(b1, b2)
