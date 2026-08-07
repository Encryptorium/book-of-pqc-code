"""Tests for the RegevParams dataclass."""

import pytest

from regev_pke import RegevParams


def test_valid_construction(toy):
    assert toy.n == 4
    assert toy.q == 97
    assert toy.m == 8
    assert toy.noise_bound == 1


def test_non_int_n_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=4.0, q=97, m=8, noise_bound=1)  # type: ignore[arg-type]


def test_non_int_q_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=4, q=97.0, m=8, noise_bound=1)  # type: ignore[arg-type]


def test_n_less_than_one_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=0, q=97, m=8, noise_bound=1)


def test_q_less_than_two_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=4, q=1, m=8, noise_bound=1)


def test_m_less_than_one_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=4, q=97, m=0, noise_bound=1)


def test_negative_noise_bound_raises():
    with pytest.raises(AssertionError):
        RegevParams(n=4, q=97, m=8, noise_bound=-1)


def test_noise_bound_too_large_for_q_raises():
    # 2B + 1 must be strictly less than q, so for q=5 the largest
    # allowed B is 1. B=2 gives 2*2+1 = 5 == q and must be rejected.
    with pytest.raises(AssertionError):
        RegevParams(n=4, q=5, m=8, noise_bound=2)


def test_noise_budget_headroom_positive_for_feasible_params(toy):
    # (97 // 2) / 2 - 8*1 = 24.0 - 8 = 16.0 > 0
    assert toy.noise_budget_headroom() == pytest.approx(16.0)
    assert toy.is_noise_budget_feasible() is True


def test_noise_budget_headroom_negative_for_infeasible_params():
    broken = RegevParams(n=4, q=13, m=8, noise_bound=1)
    # (13 // 2) / 2 - 8*1 = 3.0 - 8 = -5.0 < 0
    assert broken.noise_budget_headroom() == pytest.approx(-5.0)
    assert broken.is_noise_budget_feasible() is False
