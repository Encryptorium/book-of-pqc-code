"""Tests for the centered binomial distribution sampler (FIPS 203 Alg 8).

Covers cbd_eta's structural asserts, known-input output on all-zero
bytes, the exact symmetry of the map, zero-mean and variance eta/2
properties on a large sample, and nonce-based determinism of
sample_poly_cbd.

The symmetry test is exact rather than sampled, and it has to be:
support, mean and variance do not imply a symmetric distribution.
P(-1) = 1/3, P(0) = 1/2, P(2) = 1/6 has mean zero, variance one and
support inside {-2, ..., 2}, and is not symmetric. What is tested
instead is the structural identity that produces the symmetry, that
swapping the two eta-bit halves of every coefficient's input negates
every output.
"""

import numpy as np
import pytest

from mlkem.sampling import cbd_eta, sample_poly_cbd
from mlkem.ntt import Q, N


class TestCbdStructure:
    def test_all_zero_bytes_give_zero_polynomial(self) -> None:
        for eta in (2, 3):
            f = cbd_eta(b"\x00" * (64 * eta), eta)
            assert f.shape == (N,)
            assert np.all(f == 0)

    def test_all_one_bytes_give_zero_polynomial(self) -> None:
        # Every bit is 1, so x - y = eta - eta = 0 for every coefficient.
        for eta in (2, 3):
            f = cbd_eta(b"\xff" * (64 * eta), eta)
            assert np.all(f == 0)

    def test_wrong_length_rejected(self) -> None:
        with pytest.raises(AssertionError, match="byte_string length"):
            cbd_eta(b"\x00" * 10, eta=2)

    def test_bad_eta_rejected(self) -> None:
        with pytest.raises(AssertionError, match="eta must be 2 or 3"):
            cbd_eta(b"\x00" * 64, eta=1)


class TestCbdStatistics:
    """Expected distribution: coefficients in {-eta, ..., eta},
    symmetric around zero, variance eta / 2."""

    @pytest.mark.parametrize("eta", [2, 3])
    def test_coefficients_in_expected_range(self, eta: int) -> None:
        rng = np.random.default_rng(seed=20260411)
        samples: list[int] = []
        for _ in range(40):
            byte_string = rng.integers(
                0, 256, size=64 * eta, dtype=np.uint8
            ).tobytes()
            f = cbd_eta(byte_string, eta)
            # Put coefficients in symmetric representatives.
            sym = np.where(f > Q // 2, f - Q, f)
            samples.extend(sym.tolist())
        assert min(samples) >= -eta
        assert max(samples) <= eta

    @pytest.mark.parametrize(("eta", "tol"), [(2, 0.1), (3, 0.1)])
    def test_mean_and_variance(self, eta: int, tol: float) -> None:
        rng = np.random.default_rng(seed=7)
        samples: list[int] = []
        for _ in range(80):
            byte_string = rng.integers(
                0, 256, size=64 * eta, dtype=np.uint8
            ).tobytes()
            f = cbd_eta(byte_string, eta)
            sym = np.where(f > Q // 2, f - Q, f)
            samples.extend(sym.tolist())
        arr = np.array(samples, dtype=np.float64)
        assert abs(arr.mean()) < tol, (
            f"CBD_{eta} mean {arr.mean()} not within {tol} of 0"
        )
        # Variance of CBD_eta is eta / 2 exactly.
        expected_var = eta / 2
        assert abs(arr.var() - expected_var) < 0.1


class TestSamplePolyCbd:
    def test_deterministic(self) -> None:
        seed = b"\x01" * 32
        a = sample_poly_cbd(2, seed, 0)
        b = sample_poly_cbd(2, seed, 0)
        assert np.array_equal(a, b)

    def test_nonce_acts_as_domain_separator(self) -> None:
        seed = b"\x02" * 32
        a = sample_poly_cbd(2, seed, 0)
        b = sample_poly_cbd(2, seed, 1)
        assert not np.array_equal(a, b)

    def test_output_length_is_256(self) -> None:
        f = sample_poly_cbd(3, b"\x03" * 32, 0)
        assert f.shape == (N,)


def test_swapping_the_two_eta_bit_halves_negates_every_coefficient() -> None:
    """The exact identity behind CBD's symmetry, at both eta values.

    ``cbd_eta`` sets f_i to popcount(first eta bits) - popcount(next eta
    bits).  Exchanging those two groups therefore negates f_i, for every
    i and every input, with no sampling involved.  A distribution whose
    generating map has this property is symmetric; the moment tests
    elsewhere in this file do not establish that on their own.
    """
    for eta in (2, 3):
        rng = np.random.default_rng(seed=11)
        raw = bytes(rng.integers(0, 256, size=64 * eta, dtype=np.uint8))
        bits = np.unpackbits(
            np.frombuffer(raw, dtype=np.uint8), bitorder="little"
        )
        swapped = bits.copy()
        for i in range(256):
            lo = slice(2 * i * eta, 2 * i * eta + eta)
            hi = slice(2 * i * eta + eta, 2 * i * eta + 2 * eta)
            swapped[lo], swapped[hi] = bits[hi].copy(), bits[lo].copy()
        raw_swapped = np.packbits(swapped, bitorder="little").tobytes()

        original = _centered(cbd_eta(raw, eta))
        negated = _centered(cbd_eta(raw_swapped, eta))
        assert np.array_equal(original, -negated), (
            f"eta={eta}: swapping the halves must negate every coefficient"
        )
        # Not vacuous: the input really does change, and so does the output.
        assert raw_swapped != raw
        assert original.any()


def _centered(arr: np.ndarray) -> np.ndarray:
    """Map the canonical [0, q) representation back to {-eta, ..., eta}."""
    return np.where(arr > Q // 2, arr - Q, arr)
