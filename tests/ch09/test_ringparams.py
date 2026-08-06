"""Tests for RingParams and ModuleParams validation."""

import pytest

from ring_lwe import RingParams, ModuleParams


def test_ring_params_constructs_at_toy_primary() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    assert params.n == 4
    assert params.q == 17
    assert params.m == 4
    assert params.noise_bound == 1


def test_ring_params_constructs_at_toy_secondary() -> None:
    params = RingParams(n=8, q=17, m=8, noise_bound=1)
    assert params.n == 8
    assert params.q == 17


def test_ring_params_accepts_ml_kem_ring_with_ntt_flag_false() -> None:
    # ML-KEM's ring has n = 256 and q = 3329. Here 2n = 512 does NOT
    # divide q - 1 = 3328 (3328 = 256 * 13), so a primitive 512-th
    # root of unity does not exist in Z_3329 and the full negacyclic
    # NTT does not apply. The ring itself is still well-defined, so
    # RingParams constructs successfully; ntt_available reports the
    # absence. Chapter 11 covers the partial NTT that ML-KEM uses.
    params = RingParams(n=256, q=3329, m=1, noise_bound=2)
    assert params.n == 256
    assert params.ntt_available() is False


def test_ring_params_ntt_available_for_toy_primary() -> None:
    params = RingParams(n=4, q=17, m=4, noise_bound=1)
    assert params.ntt_available() is True


def test_ring_params_rejects_q_without_2n_divides_q_minus_1() -> None:
    # 4 is a power of 2 and 11 is prime, but 2n = 8 does not divide
    # q - 1 = 10, so the full negacyclic NTT is unavailable. The
    # RingParams constructs (the ring exists), but ntt_available is
    # False. This separates the ring-existence condition from the
    # NTT-availability condition.
    params = RingParams(n=4, q=11, m=4, noise_bound=1)
    assert params.ntt_available() is False


def test_ring_params_rejects_non_power_of_two_n() -> None:
    with pytest.raises(AssertionError, match="power of two"):
        RingParams(n=3, q=17, m=3, noise_bound=1)


def test_ring_params_rejects_composite_q() -> None:
    with pytest.raises(AssertionError, match="prime"):
        RingParams(n=4, q=15, m=4, noise_bound=1)


def test_ring_params_rejects_noise_too_wide() -> None:
    # 2B + 1 must be strictly less than q. At q = 17 and B = 8,
    # 2*8 + 1 = 17, which is not strictly less.
    with pytest.raises(AssertionError, match="2B \\+ 1 < q"):
        RingParams(n=4, q=17, m=4, noise_bound=8)


def test_ring_params_rejects_negative_noise_bound() -> None:
    with pytest.raises(AssertionError, match="nonnegative"):
        RingParams(n=4, q=17, m=4, noise_bound=-1)


def test_ring_params_rejects_n_equal_one() -> None:
    # n = 1 is technically a power of two but the ring collapses to
    # Z_q, so the package rejects it.
    with pytest.raises(AssertionError, match="n >= 2"):
        RingParams(n=1, q=17, m=1, noise_bound=0)


def test_module_params_constructs_at_ml_kem_512_rank() -> None:
    params = ModuleParams(n=4, q=17, k=2, m=4, noise_bound=1)
    assert params.k == 2


def test_module_params_rejects_k_zero() -> None:
    with pytest.raises(AssertionError, match="k >= 1"):
        ModuleParams(n=4, q=17, k=0, m=4, noise_bound=1)


def test_module_params_as_ring_params() -> None:
    params = ModuleParams(n=4, q=17, k=3, m=5, noise_bound=1)
    rparams = params.as_ring_params()
    assert rparams.n == 4
    assert rparams.q == 17
    assert rparams.m == 5
    assert rparams.noise_bound == 1
