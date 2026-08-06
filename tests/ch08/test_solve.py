"""Tests for noise-free Gaussian elimination over Z_q."""

import numpy as np

from lwe import (
    LWEParams,
    sample_secret,
    sample_lwe,
    gaussian_eliminate_mod_q,
)


def test_recovers_secret_on_noise_free_instance(toy):
    rng = np.random.default_rng(seed=0)
    s = sample_secret(toy, rng)
    # Sample A, but form b without any error.
    A = rng.integers(low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64)
    b = (A @ s) % toy.q
    recovered = gaussian_eliminate_mod_q(A, b, toy.q)
    assert recovered is not None
    assert np.array_equal(recovered, s)


def test_recovers_over_many_random_seeds(toy):
    # Stress-test the recovery on 25 random noise-free instances.
    for seed in range(25):
        rng = np.random.default_rng(seed=seed)
        s = sample_secret(toy, rng)
        A = rng.integers(
            low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64
        )
        b = (A @ s) % toy.q
        recovered = gaussian_eliminate_mod_q(A, b, toy.q)
        assert recovered is not None, f"failed to recover s for seed={seed}"
        assert np.array_equal(recovered, s), f"wrong s for seed={seed}"


def test_recovers_minimal_square_case():
    # When m == n the system is exactly determined: no consistency rows.
    params = LWEParams(n=4, q=97, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=7)
    s = sample_secret(params, rng)
    A = rng.integers(
        low=0, high=params.q, size=(params.m, params.n), dtype=np.int64
    )
    b = (A @ s) % params.q
    recovered = gaussian_eliminate_mod_q(A, b, params.q)
    assert recovered is not None
    assert np.array_equal(recovered, s)
