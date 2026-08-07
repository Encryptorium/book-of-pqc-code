"""Tests for ByteEncode_d / ByteDecode_d (FIPS 203 §4.2.1 Algorithms 5-6).

Covers round-trip for d in {1, 4, 10, 11, 12}, output byte lengths,
rejection of out-of-range input, the d=12 mod-q reduction behavior,
and the vector encode/decode helpers.
"""

import numpy as np
import pytest

from mlkem.serialize import (
    byte_encode_d,
    byte_decode_d,
    byte_encode_vector,
    byte_decode_vector,
)
from mlkem.ntt import Q, N
from mlkem.compress import compress, decompress


class TestByteEncodeLengths:
    @pytest.mark.parametrize("d", [1, 4, 10, 11, 12])
    def test_output_length_is_32d(self, d: int) -> None:
        if d == 12:
            f = np.zeros(N, dtype=np.int64)
        else:
            f = np.zeros(N, dtype=np.int64)
        out = byte_encode_d(f, d)
        assert len(out) == 32 * d


class TestRoundTripUncompressed:
    @pytest.mark.parametrize("seed", [0, 1, 20260411])
    def test_d12_round_trip(self, seed: int) -> None:
        rng = np.random.default_rng(seed=seed)
        f = rng.integers(0, Q, size=N, dtype=np.int64)
        encoded = byte_encode_d(f, 12)
        decoded = byte_decode_d(encoded, 12)
        assert np.array_equal(decoded, f)


class TestRoundTripCompressed:
    """For d < 12, inputs must be in [0, 2^d)."""

    @pytest.mark.parametrize("d", [1, 4, 10, 11])
    def test_uniform_in_range_round_trip(self, d: int) -> None:
        rng = np.random.default_rng(seed=20260411)
        two_d = 1 << d
        f = rng.integers(0, two_d, size=N, dtype=np.int64)
        encoded = byte_encode_d(f, d)
        decoded = byte_decode_d(encoded, d)
        assert np.array_equal(decoded, f)

    @pytest.mark.parametrize("d", [1, 4, 10, 11])
    def test_compress_encode_decode_decompress(self, d: int) -> None:
        """The full pipeline: Z_q → Z_{2^d} → bytes → Z_{2^d} → Z_q."""
        rng = np.random.default_rng(seed=42)
        f = rng.integers(0, Q, size=N, dtype=np.int64)
        compressed = compress(f, d)
        encoded = byte_encode_d(compressed, d)
        decoded = byte_decode_d(encoded, d)
        assert np.array_equal(decoded, compressed)


class TestRejection:
    def test_out_of_range_at_d_less_than_12_rejected(self) -> None:
        f = np.zeros(N, dtype=np.int64)
        f[0] = 16  # outside [0, 16) for d = 4.
        with pytest.raises(AssertionError):
            byte_encode_d(f, 4)

    def test_out_of_range_at_d12_rejected(self) -> None:
        f = np.zeros(N, dtype=np.int64)
        f[0] = Q  # outside [0, q).
        with pytest.raises(AssertionError):
            byte_encode_d(f, 12)


class TestD12ModQ:
    def test_decode_reduces_mod_q(self) -> None:
        # Construct a 12-bit field whose value is q+1 = 3330 (larger
        # than q but representable in 12 bits). ByteDecode_12 must
        # reduce this to 1.
        f = np.zeros(N, dtype=np.int64)
        f[0] = 1  # encodes to 0x01 in the first 12 bits
        encoded = bytearray(byte_encode_d(f, 12))
        # Overwrite the first 12 bits to encode 3330 (0xD02).
        encoded[0] = 0x02
        encoded[1] = (encoded[1] & 0xF0) | 0x0D
        decoded = byte_decode_d(bytes(encoded), 12)
        assert int(decoded[0]) == 3330 % Q


class TestVectorEncode:
    def test_k2_round_trip(self) -> None:
        rng = np.random.default_rng(seed=20260411)
        fs = rng.integers(0, Q, size=(2, N), dtype=np.int64)
        encoded = byte_encode_vector(fs, 12)
        assert len(encoded) == 32 * 12 * 2
        decoded = byte_decode_vector(encoded, 12, k=2)
        assert np.array_equal(decoded, fs)

    def test_k3_compressed_round_trip(self) -> None:
        rng = np.random.default_rng(seed=20260411)
        fs = rng.integers(0, 1 << 10, size=(3, N), dtype=np.int64)
        encoded = byte_encode_vector(fs, 10)
        assert len(encoded) == 32 * 10 * 3
        decoded = byte_decode_vector(encoded, 10, k=3)
        assert np.array_equal(decoded, fs)
