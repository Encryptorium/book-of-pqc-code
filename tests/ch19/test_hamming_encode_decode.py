"""Tests for Hamming [7,4,3] encode and decode."""

import itertools

from coding_theory.hamming import encode, decode, syndrome


def test_all_messages_encode_to_length_7():
    """All 16 possible 4-bit messages encode to 7-bit codewords."""
    for bits in itertools.product([0, 1], repeat=4):
        cw = encode(list(bits))
        assert len(cw) == 7
        assert all(b in (0, 1) for b in cw)


def test_single_error_correction():
    """Flipping any single bit in any codeword is corrected by decode."""
    for bits in itertools.product([0, 1], repeat=4):
        msg = list(bits)
        cw = encode(msg)
        for pos in range(7):
            received = list(cw)
            received[pos] ^= 1
            recovered = decode(received)
            assert recovered == msg, (
                f"msg={msg}, error at pos={pos}: got {recovered}"
            )


def test_no_error_roundtrip():
    """Encoding then decoding without errors recovers the message."""
    for bits in itertools.product([0, 1], repeat=4):
        msg = list(bits)
        cw = encode(msg)
        assert decode(cw) == msg


def test_codeword_has_zero_syndrome():
    """Every valid codeword has the zero syndrome."""
    for bits in itertools.product([0, 1], repeat=4):
        cw = encode(list(bits))
        s = syndrome(cw)
        assert s == [0, 0, 0]
