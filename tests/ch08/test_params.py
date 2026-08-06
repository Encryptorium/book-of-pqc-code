"""Tests for the LWEParams dataclass."""

import pytest

from lwe import LWEParams


def test_valid_toy_params():
    p = LWEParams(n=4, q=97, m=8, noise_bound=1)
    assert p.n == 4
    assert p.q == 97
    assert p.m == 8
    assert p.noise_bound == 1


def test_rejects_zero_dimension():
    with pytest.raises(AssertionError):
        LWEParams(n=0, q=97, m=8, noise_bound=1)


def test_rejects_modulus_less_than_two():
    with pytest.raises(AssertionError):
        LWEParams(n=4, q=1, m=8, noise_bound=1)


def test_rejects_m_below_n():
    with pytest.raises(AssertionError):
        LWEParams(n=4, q=97, m=3, noise_bound=1)


def test_rejects_negative_noise_bound():
    with pytest.raises(AssertionError):
        LWEParams(n=4, q=97, m=8, noise_bound=-1)


def test_rejects_noise_bound_exceeding_modulus():
    # 2B + 1 must be strictly less than q
    with pytest.raises(AssertionError):
        LWEParams(n=4, q=5, m=8, noise_bound=3)


def test_rejects_noise_bound_at_boundary():
    # Exact boundary 2B + 1 == q is invalid: the error distribution
    # would be indistinguishable from uniform over Z_q.
    with pytest.raises(AssertionError):
        LWEParams(n=4, q=5, m=8, noise_bound=2)


def test_rejects_non_integer_fields():
    with pytest.raises(AssertionError):
        LWEParams(n=4.0, q=97, m=8, noise_bound=1)  # type: ignore[arg-type]
