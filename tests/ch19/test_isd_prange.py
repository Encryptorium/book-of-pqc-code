"""Tests for Prange ISD and cost estimation."""

import random

from coding_theory.hamming import parity_check_matrix, encode, syndrome
from coding_theory.gf2 import weight
from coding_theory.isd import prange_isd, isd_cost_estimate, isd_exponent


def test_prange_finds_weight1_error_in_hamming():
    """Prange ISD recovers a planted single-bit error in the [7,4,3] Hamming code."""
    H = parity_check_matrix()
    cw = encode([1, 0, 1, 1])
    for pos in range(7):
        received = list(cw)
        received[pos] ^= 1
        s = syndrome(received)
        e, iters = prange_isd(H, s, target_weight=1, rng=random.Random(42))
        assert weight(e) == 1
        assert e[pos] == 1


def test_prange_isd_cost_hamming():
    """For [7,4,3] with w=1 (a perfect code), expected iterations ~ C(7,4)/C(6,4) = 35/15 ~ 2.33."""
    cost = isd_cost_estimate(7, 4, 1)
    assert 2.0 < cost < 3.0


def test_isd_exponent_mceliece348864():
    """Prange exponent for mceliece348864 (n=3488, k=2720, w=64) is approximately 143."""
    exp = isd_exponent(3488, 2720, 64)
    assert 140 < exp < 150


def test_isd_exponent_increases_with_weight():
    """Higher error weight means more ISD iterations for the same code."""
    # Use a moderately sized code
    exp1 = isd_exponent(127, 64, 10)
    exp2 = isd_exponent(127, 64, 20)
    assert exp2 > exp1
