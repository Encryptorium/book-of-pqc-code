"""Tests for ring_add and ring_mul_naive in R_q = Z_q[x]/(x^n + 1)."""

import numpy as np
import pytest

from ring_lwe import ring_add, ring_mul_naive


Q = 17


def test_ring_add_is_coefficient_wise_mod_q() -> None:
    f = np.array([1, 2, 3, 4], dtype=np.int64)
    g = np.array([16, 15, 14, 13], dtype=np.int64)
    h = ring_add(f, g, Q)
    # (1 + 16, 2 + 15, 3 + 14, 4 + 13) mod 17 = (17, 17, 17, 17) mod 17
    assert h.tolist() == [0, 0, 0, 0]


def test_ring_mul_x_times_x_cube_is_negative_one() -> None:
    # f(x) = x, g(x) = x^3. In Z[x] their product is x^4. In R_q
    # with x^4 + 1 = 0, x^4 reduces to -1 = q - 1 = 16.
    f = np.array([0, 1, 0, 0], dtype=np.int64)
    g = np.array([0, 0, 0, 1], dtype=np.int64)
    h = ring_mul_naive(f, g, Q)
    # Expected: the constant term is -1 mod 17 = 16, rest zero.
    assert h.tolist() == [16, 0, 0, 0]


def test_ring_mul_x_times_x_is_x_squared() -> None:
    # No wraparound yet at n = 4.
    f = np.array([0, 1, 0, 0], dtype=np.int64)
    g = np.array([0, 1, 0, 0], dtype=np.int64)
    h = ring_mul_naive(f, g, Q)
    assert h.tolist() == [0, 0, 1, 0]


def test_ring_mul_worked_hand_example() -> None:
    # Hand computation used in the chapter: f = 1 + 2x + 3x^2 + 4x^3,
    # g = 5 + 6x over R_{17} = Z_17[x]/(x^4 + 1).
    #
    # In Z[x] the product is:
    #   5 + 16x + 27x^2 + 38x^3 + 24x^4 + 0*x^5 + 0*x^6
    #     = 5 + 16x + 27x^2 + 38x^3 + 24x^4
    # Reduce x^4 -> -1: subtract 24 from the constant term.
    #   constant:  5 - 24 = -19
    #   x coeff :  16
    #   x^2     :  27
    #   x^3     :  38
    # Reduce each mod 17:
    #   -19 mod 17 = 15
    #    16         = 16
    #    27         = 10
    #    38         = 4
    f = np.array([1, 2, 3, 4], dtype=np.int64)
    g = np.array([5, 6, 0, 0], dtype=np.int64)
    h = ring_mul_naive(f, g, Q)
    assert h.tolist() == [15, 16, 10, 4]


def test_ring_mul_has_exactly_n_coefficients() -> None:
    for n in (2, 4, 8):
        # Pick q admitting the ring. For n=2,4,8 with Z_17 we need
        # 2n | 16, so n in {2, 4, 8}.
        f = np.ones(n, dtype=np.int64)
        g = np.ones(n, dtype=np.int64)
        h = ring_mul_naive(f, g, Q)
        assert h.shape == (n,)


def test_ring_mul_is_commutative_on_random_seeds() -> None:
    rng = np.random.default_rng(seed=42)
    n = 4
    for _ in range(10):
        f = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        g = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        fg = ring_mul_naive(f, g, Q)
        gf = ring_mul_naive(g, f, Q)
        np.testing.assert_array_equal(fg, gf)


def test_ring_mul_is_associative_on_random_seeds() -> None:
    rng = np.random.default_rng(seed=7)
    n = 4
    for _ in range(10):
        f = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        g = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        h = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        left = ring_mul_naive(ring_mul_naive(f, g, Q), h, Q)
        right = ring_mul_naive(f, ring_mul_naive(g, h, Q), Q)
        np.testing.assert_array_equal(left, right)


def test_ring_mul_distributes_over_addition() -> None:
    rng = np.random.default_rng(seed=11)
    n = 4
    for _ in range(10):
        f = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        g = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        h = rng.integers(low=0, high=Q, size=n, dtype=np.int64)
        left = ring_mul_naive(f, ring_add(g, h, Q), Q)
        right = ring_add(
            ring_mul_naive(f, g, Q), ring_mul_naive(f, h, Q), Q
        )
        np.testing.assert_array_equal(left, right)


def test_ring_mul_shape_mismatch_fails() -> None:
    f = np.array([1, 2, 3, 4], dtype=np.int64)
    g = np.array([1, 2, 3], dtype=np.int64)
    with pytest.raises(AssertionError, match="shape mismatch"):
        ring_mul_naive(f, g, Q)
