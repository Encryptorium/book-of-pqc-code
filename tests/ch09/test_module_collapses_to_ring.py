"""Module-LWE at rank k = 1 collapses to Ring-LWE.

At k = 1, a Module-LWE sample reduces to a stack of m independent
Ring-LWE samples that share the same secret s. At k = 1 and m = 1,
the sample is exactly one Ring-LWE pair: there is an s in R_q,
exactly one element a of R_q acting as the "public" polynomial, and
b = a * s + e with e short. These tests verify the collapse both
structurally (the Module-LWE output obeys the Ring-LWE defining
identity) and semantically (at k = 1 the matrix A has shape (m, 1,
n) and the defining identity reduces to b[i] = A[i, 0] * s[0] + e[i]
in R_q).
"""

import numpy as np

from ring_lwe import (
    ModuleParams,
    ring_mul_naive,
    sample_module_lwe,
)


def test_module_lwe_at_k_equals_one_is_stack_of_ring_lwe() -> None:
    params = ModuleParams(n=4, q=17, k=1, m=3, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    # At k = 1, s has shape (1, n); unwrap it to a single ring element.
    assert s.shape == (1, 4)
    s_ring = s[0]
    # Each row of A is a single ring element wrapped in a rank-1 axis.
    for i in range(params.m):
        a_ring = A[i, 0]
        expected_b = (ring_mul_naive(a_ring, s_ring, params.q) + e[i]) % params.q
        np.testing.assert_array_equal(b[i], expected_b)


def test_module_lwe_at_k_equals_one_single_sample() -> None:
    # At (k, m) = (1, 1), a Module-LWE instance is exactly one
    # Ring-LWE pair.
    params = ModuleParams(n=4, q=17, k=1, m=1, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    assert A.shape == (1, 1, 4)
    assert s.shape == (1, 4)
    assert e.shape == (1, 4)
    assert b.shape == (1, 4)
    expected = (ring_mul_naive(A[0, 0], s[0], params.q) + e[0]) % params.q
    np.testing.assert_array_equal(b[0], expected)


def test_module_lwe_rank_two_matches_direct_formula() -> None:
    # Same check at k = 2 to pin down the rank-k matrix-vector
    # product: b[i] = A[i, 0] * s[0] + A[i, 1] * s[1] + e[i] in R_q.
    params = ModuleParams(n=4, q=17, k=2, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    for i in range(params.m):
        row = np.zeros(params.n, dtype=np.int64)
        for j in range(params.k):
            row = (row + ring_mul_naive(A[i, j], s[j], params.q)) % params.q
        expected = (row + e[i]) % params.q
        np.testing.assert_array_equal(b[i], expected)


def test_module_lwe_rank_three_matches_direct_formula() -> None:
    # Exercise 3 in the chapter plan covers rank k = 3.
    params = ModuleParams(n=4, q=17, k=3, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    A, s, e, b = sample_module_lwe(params, rng)
    for i in range(params.m):
        row = np.zeros(params.n, dtype=np.int64)
        for j in range(params.k):
            row = (row + ring_mul_naive(A[i, j], s[j], params.q)) % params.q
        expected = (row + e[i]) % params.q
        np.testing.assert_array_equal(b[i], expected)
