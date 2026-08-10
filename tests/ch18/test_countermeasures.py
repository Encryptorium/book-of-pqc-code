"""Verify-after-sign and constant-time chaining, priced in hash calls."""

import random

import pytest

from hash_cryptanalysis.countermeasures import (
    constant_time_chain_cost,
    verify_after_sign_hash_calls,
    wots_sign_hash_calls,
    wots_verify_hash_calls,
)
from hash_cryptanalysis.params import by_name


W = 16
ELL_128 = 35


def _digits(rng: random.Random, ell: int, w: int) -> list[int]:
    return [rng.randrange(w) for _ in range(ell)]


def test_chapter_parameters():
    """Chapter 18 works Exercise 4 at w = 16, ell = 35, so 525 hash calls."""
    ps = by_name("128s")
    assert ps.w == W
    assert ps.ell == ELL_128
    assert constant_time_chain_cost(ps.ell, ps.w) == 525


def test_verify_after_sign_is_constant_at_the_chapter_parameters():
    rng = random.Random(1_808)
    for _ in range(200):
        digits = _digits(rng, ELL_128, W)
        assert verify_after_sign_hash_calls(digits, W) == 525


@pytest.mark.parametrize(
    "digits",
    [
        [0] * ELL_128,
        [W - 1] * ELL_128,
        list(range(ELL_128)),
        [i % W for i in range(ELL_128)],
    ],
)
def test_verify_after_sign_ignores_the_digits(digits):
    """The extremes included: an all-zero and an all-maximum digit vector."""
    assert verify_after_sign_hash_calls(digits, W) == constant_time_chain_cost(
        len(digits), W
    )


def test_sign_and_verify_costs_are_complements():
    rng = random.Random(2_026)
    for _ in range(100):
        digits = _digits(rng, ELL_128, W)
        assert wots_sign_hash_calls(digits) + wots_verify_hash_calls(digits, W) == 525


def test_sign_cost_is_the_digit_sum():
    assert wots_sign_hash_calls([0, 1, 2, 3]) == 6
    assert wots_sign_hash_calls([]) == 0


def test_verify_cost_is_the_complement_of_the_digit_sum():
    assert wots_verify_hash_calls([0, 1, 2, 3], W) == 4 * (W - 1) - 6
    assert wots_verify_hash_calls([W - 1] * 4, W) == 0


def test_cheap_to_sign_is_dear_to_verify():
    """The two costs move in opposite directions, digit for digit."""
    low = [0] * ELL_128
    high = [W - 1] * ELL_128
    assert wots_sign_hash_calls(low) < wots_sign_hash_calls(high)
    assert wots_verify_hash_calls(low, W) > wots_verify_hash_calls(high, W)


@pytest.mark.parametrize("short", ["128s", "192s", "256s", "128f", "192f", "256f"])
def test_constant_time_cost_scales_with_ell(short):
    ps = by_name(short)
    assert constant_time_chain_cost(ps.ell, ps.w) == ps.ell * 15


def test_verify_after_sign_roughly_doubles_signing():
    """Average signing walks (w - 1) / 2 steps per chain, so the total is about 2x."""
    rng = random.Random(205)
    digits = _digits(rng, 4_000, W)
    average_sign = wots_sign_hash_calls(digits)
    total = verify_after_sign_hash_calls(digits, W)
    assert 1.9 < total / average_sign < 2.1
