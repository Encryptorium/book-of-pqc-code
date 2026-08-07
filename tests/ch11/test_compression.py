"""Tests for compress, decompress, and message lifting (FIPS 203 §4.2).

Covers correctness at the edge cases (0 and q-1), the compression
noise bound, coefficient-wise application on numpy arrays, and the
message-to-polynomial round trip.
"""

import numpy as np
import pytest

from mlkem.compress import (
    compress,
    decompress,
    compression_noise_bound,
    message_to_poly,
    poly_to_message,
)
from mlkem.ntt import Q, N


class TestCompressScalar:
    def test_compress_zero(self) -> None:
        for d in range(1, 12):
            out = int(compress(np.array([0]), d)[0])
            assert out == 0, f"compress(0, {d}) should be 0, got {out}"

    def test_compress_q_minus_one_on_cycle(self) -> None:
        # q - 1 sits between the last bucket (index 2^d - 1) and the
        # first bucket (index 0 ≡ q). Whether it rounds to 0 or
        # 2^d - 1 depends on whether 2^d / q < 1 or >= 1.
        # For d in {1, ..., 10} we have 2^d < q so the rounding goes
        # to 0; for d = 11 we have 2^11 > q so the result is 2^d - 1
        # under round-half-up.
        for d in range(1, 11):
            out = int(compress(np.array([Q - 1]), d)[0])
            assert out == 0, f"compress(q-1, d={d}) expected 0, got {out}"
        assert int(compress(np.array([Q - 1]), 11)[0]) == 2047

    def test_compress_d1_decoding_regions(self) -> None:
        # At d = 1, compress(x, 1) = round-half-up(2x/q) mod 2. With
        # q = 3329, x * 2 / q crosses 0.5 at x = 832.25 and crosses
        # 1.5 at x = 2496.75. Under floor((2x + q/2) / q), the exact
        # integer boundaries are: 832 maps to 0, 833 maps to 1, 2496
        # maps to 1, 2497 maps to 0.
        assert int(compress(np.array([832]), 1)[0]) == 0
        assert int(compress(np.array([833]), 1)[0]) == 1
        assert int(compress(np.array([2496]), 1)[0]) == 1
        assert int(compress(np.array([2497]), 1)[0]) == 0

    def test_compress_maps_into_range(self) -> None:
        for d in (1, 4, 10, 11):
            values = np.arange(Q)
            out = compress(values, d)
            assert out.min() >= 0
            assert out.max() < (1 << d)


class TestDecompressScalar:
    def test_decompress_zero(self) -> None:
        for d in range(1, 12):
            assert int(decompress(np.array([0]), d)[0]) == 0

    def test_decompress_one_at_d1(self) -> None:
        # Decompress_q(1, 1) = round(q/2) = 1665 for q = 3329.
        assert int(decompress(np.array([1]), 1)[0]) == 1665

    def test_decompress_max_at_d4(self) -> None:
        # Decompress_q(15, 4) = round(15 * 3329 / 16) = 3121
        assert int(decompress(np.array([15]), 4)[0]) == 3121


class TestCompressDecompressError:
    @pytest.mark.parametrize("d", [1, 4, 10, 11])
    def test_round_trip_error_bounded(self, d: int) -> None:
        """|Decompress(Compress(x, d), d) - x| <= ceil(q / 2^{d+1}) for
        every x in Z_q (in symmetric representatives)."""
        bound = compression_noise_bound(d)
        xs = np.arange(Q, dtype=np.int64)
        round_trip = decompress(compress(xs, d), d)
        diff = (round_trip - xs) % Q
        sym = np.where(diff > Q // 2, diff - Q, diff)
        assert int(np.max(np.abs(sym))) <= bound

    def test_noise_bound_values(self) -> None:
        # q = 3329. ceil(3329 / 2) = 1665 at d=0 (unused), ceil(3329/4) = 833
        # at d=1, ceil(3329/2048) = 2 at d=10, ceil(3329/4096) = 1 at d=11.
        assert compression_noise_bound(1) == 833
        assert compression_noise_bound(4) == 105
        assert compression_noise_bound(10) == 2
        assert compression_noise_bound(11) == 1


class TestCompressArray:
    def test_coefficient_wise(self) -> None:
        xs = np.array([0, 1, 1664, 1665, 3328])
        out = compress(xs, 1)
        # compress(x, 1) = floor((2x + 1664) / 3329) mod 2:
        # x=0 -> 0; x=1 -> 0; x=1664 -> 1; x=1665 -> 1; x=3328 -> 0.
        expected = np.array([0, 0, 1, 1, 0])
        assert np.array_equal(out, expected)


class TestMessagePoly:
    def test_round_trip(self) -> None:
        rng = np.random.default_rng(seed=20260411)
        for _ in range(20):
            m = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
            f = message_to_poly(m)
            recovered = poly_to_message(f)
            assert recovered == m

    def test_message_coefficients_are_0_or_1665(self) -> None:
        m = bytes(range(32))
        f = message_to_poly(m)
        uniq = set(int(c) for c in f)
        assert uniq <= {0, 1665}

    def test_zero_message_gives_zero_poly(self) -> None:
        f = message_to_poly(b"\x00" * 32)
        assert int(f.sum()) == 0
