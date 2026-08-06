"""Tests for the negacyclic NTT."""

import numpy as np

from ring_lwe import (
    RingParams,
    ntt_forward,
    ntt_inverse,
    ring_mul_ntt,
    ring_mul_naive,
    primitive_2n_root,
)


def test_primitive_2n_root_n4_q17_is_two() -> None:
    psi = primitive_2n_root(4, 17)
    assert psi == 2
    # Verify: 2^8 mod 17 = 1 and 2^4 mod 17 = 16 != 1.
    assert pow(psi, 8, 17) == 1
    assert pow(psi, 4, 17) != 1


def test_primitive_2n_root_n8_q17_is_three() -> None:
    psi = primitive_2n_root(8, 17)
    assert psi == 3
    # 3 has order 16 mod 17: 3^16 = 1, 3^8 = 16 != 1.
    assert pow(psi, 16, 17) == 1
    assert pow(psi, 8, 17) != 1


def test_primitive_2n_root_rejects_ml_kem_ring() -> None:
    # For ML-KEM's (n, q) = (256, 3329) the condition 2n | q - 1
    # fails: 3328 = 256 * 13, so 512 does not divide 3328. The
    # helper raises rather than returning a non-primitive element.
    # ML-KEM's partial NTT uses a 256-th root instead and is a Ch 11
    # concern.
    import pytest

    with pytest.raises(AssertionError, match="512"):
        primitive_2n_root(256, 3329)


def test_ntt_forward_rejects_params_without_full_ntt() -> None:
    # RingParams(n=4, q=11) constructs fine (the ring exists) but
    # the full NTT is unavailable because 2n = 8 does not divide
    # q - 1 = 10.
    import pytest

    params = RingParams(n=4, q=11, m=1, noise_bound=1)
    assert params.ntt_available() is False
    f = np.array([1, 2, 3, 4], dtype=np.int64)
    with pytest.raises(AssertionError, match="8"):
        ntt_forward(f, params)


def test_ntt_round_trip_n4_q17() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=0)
    for _ in range(20):
        f = rng.integers(low=0, high=17, size=4, dtype=np.int64)
        fhat = ntt_forward(f, params)
        f_back = ntt_inverse(fhat, params)
        np.testing.assert_array_equal(f, f_back)


def test_ntt_round_trip_n8_q17() -> None:
    params = RingParams(n=8, q=17, m=8, noise_bound=1)
    rng = np.random.default_rng(seed=1)
    for _ in range(20):
        f = rng.integers(low=0, high=17, size=8, dtype=np.int64)
        fhat = ntt_forward(f, params)
        f_back = ntt_inverse(fhat, params)
        np.testing.assert_array_equal(f, f_back)


def test_ntt_of_x_at_n4_q17_matches_plan_exercise() -> None:
    # Planned exercise 2 from the chapter plan: the NTT of f = x at
    # (n, q, psi) = (4, 17, 2) equals (psi, psi^3, psi^5, psi^7) =
    # (2, 8, 15, 9).
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    f = np.array([0, 1, 0, 0], dtype=np.int64)
    fhat = ntt_forward(f, params)
    assert fhat.tolist() == [2, 8, 15, 9]


def test_ntt_of_constant_one_is_all_ones_at_n4_q17() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    f = np.array([1, 0, 0, 0], dtype=np.int64)
    fhat = ntt_forward(f, params)
    # The constant polynomial 1 evaluates to 1 at every root.
    assert fhat.tolist() == [1, 1, 1, 1]


def test_ring_mul_ntt_matches_ring_mul_naive_n4_q17() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    rng = np.random.default_rng(seed=2)
    for _ in range(30):
        f = rng.integers(low=0, high=17, size=4, dtype=np.int64)
        g = rng.integers(low=0, high=17, size=4, dtype=np.int64)
        via_ntt = ring_mul_ntt(f, g, params)
        via_naive = ring_mul_naive(f, g, 17)
        np.testing.assert_array_equal(via_ntt, via_naive)


def test_ring_mul_ntt_matches_ring_mul_naive_n8_q17() -> None:
    params = RingParams(n=8, q=17, m=8, noise_bound=1)
    rng = np.random.default_rng(seed=3)
    for _ in range(30):
        f = rng.integers(low=0, high=17, size=8, dtype=np.int64)
        g = rng.integers(low=0, high=17, size=8, dtype=np.int64)
        via_ntt = ring_mul_ntt(f, g, params)
        via_naive = ring_mul_naive(f, g, 17)
        np.testing.assert_array_equal(via_ntt, via_naive)


def test_ring_mul_ntt_on_worked_hand_example() -> None:
    # Same hand example as test_ring.py::test_ring_mul_worked_hand_example.
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    f = np.array([1, 2, 3, 4], dtype=np.int64)
    g = np.array([5, 6, 0, 0], dtype=np.int64)
    h = ring_mul_ntt(f, g, params)
    assert h.tolist() == [15, 16, 10, 4]
