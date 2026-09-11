"""Tests for the repetition code (encode and majority-vote decode)."""

from hqc.repetition import rep_encode, rep_decode


N = 83
R = 17
K = N // R   # 4


def test_rep_encode_single_bit():
    msg = [1] + [0] * (K - 1)
    codeword = rep_encode(msg, R, N)
    assert codeword[:R] == [1] * R
    assert codeword[R:2 * R] == [0] * R
    assert len(codeword) == N


def test_rep_encode_length():
    msg = [1, 0, 1, 1]
    codeword = rep_encode(msg, R, N)
    assert len(codeword) == N


def test_rep_decode_clean():
    msg = [1, 0, 1, 1]
    codeword = rep_encode(msg, R, N)
    recovered = rep_decode(codeword, R, N)
    assert recovered == msg


def test_rep_decode_with_errors():
    """floor((R-1)/2) = 8 errors in EVERY block; should still decode.

    The per-block claim is the one worth making, and it needs every block
    corrupted. Damaging only the first block leaves the rest of the word
    pristine, which is a weaker fixture than the name promises.
    """
    msg = [1, 0, 1, 0]
    codeword = rep_encode(msg, R, N)
    corrupted = list(codeword)
    for block in range(len(msg)):
        base = block * R
        for i in range(8):
            corrupted[base + i] = 1 - corrupted[base + i]
    # Every block really is damaged, and by the full budget.
    for block in range(len(msg)):
        base = block * R
        flipped = sum(
            1
            for i in range(R)
            if corrupted[base + i] != codeword[base + i]
        )
        assert flipped == 8
    recovered = rep_decode(corrupted, R, N)
    assert recovered == msg


def test_rep_decode_too_many_errors():
    """Introduce 9 errors in a block of 17; majority vote flips."""
    msg = [1, 0, 0, 0]
    codeword = rep_encode(msg, R, N)
    corrupted = list(codeword)
    # First block is 17 ones. Flip 9 -> 8 ones, 9 zeros.
    for i in range(9):
        corrupted[i] = 0
    recovered = rep_decode(corrupted, R, N)
    assert recovered[0] == 0   # Decoding error as expected


def test_rep_roundtrip_all_messages():
    """All 2^k = 16 possible messages round-trip through clean encode/decode."""
    for i in range(2**K):
        msg = [(i >> b) & 1 for b in range(K)]
        codeword = rep_encode(msg, R, N)
        recovered = rep_decode(codeword, R, N)
        assert recovered == msg, f"Failed for message {msg}"
