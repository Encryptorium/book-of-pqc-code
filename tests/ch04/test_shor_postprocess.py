"""Tests for the classical post-processing step of Shor's algorithm in
``classical.shor_postprocess``.
"""

import pytest

from classical.shor_postprocess import recover_factor


def test_worked_example_n323():
    # N = 17 * 19 = 323. The order of 2 modulo 323 is 72.
    # 2^36 mod 323 = 305, and gcd(304, 323) = 19.
    factor = recover_factor(323, 2, 72)
    assert factor in (17, 19)
    assert 323 % factor == 0


def test_larger_toy_n3233():
    # N = 53 * 61 = 3233. The multiplicative order of 10 modulo 3233 is 780.
    factor = recover_factor(3233, 10, 780)
    assert factor in (53, 61)
    assert 3233 % factor == 0


def test_odd_period_rejected():
    # An odd period means the classical Shor would retry with a new base.
    with pytest.raises(ValueError, match="odd"):
        recover_factor(323, 2, 71)


def test_bad_period_rejected():
    # r is even but a^(r/2) mod n == n - 1: the post-processing yields
    # only trivial factors and the classical Shor retries.
    # For n = 15, a = 4: 4^1 mod 15 = 4, 4^2 mod 15 = 1, so the true
    # period is 2 and 4^1 == 4 != 14, so this works. Instead pick a
    # contrived case where a^(r/2) == n - 1 by construction: n = 21,
    # a = 20, r = 2, then 20^1 mod 21 = 20 = n - 1.
    with pytest.raises(ValueError):
        recover_factor(21, 20, 2)


def test_trivial_square_root_from_below_rejected():
    # If r is a multiple of the true order and r/2 is itself a multiple
    # of the order, then a^(r/2) == 1 mod n, both gcd candidates are
    # trivial, and the post-processing raises ValueError so the
    # classical Shor loop retries with a new base.
    # Worked example: n = 21 = 3 * 7, a = 2, ord(2) = 6, pick r = 12.
    # Then a^(r/2) = 2^6 mod 21 = 1, gcd(0, 21) = 21, gcd(2, 21) = 1.
    with pytest.raises(ValueError):
        recover_factor(21, 2, 12)
