"""Pins the [7, 4] Hamming decode Chapter 3's second exercise asks for."""

from hard_problems.codes import (
    decode_hamming_syndrome,
    hamming_parity_check,
    syndrome,
)


def test_parity_check_columns_are_the_integers_one_to_seven():
    """Column j - 1 is the binary representation of j, most significant first."""
    h = hamming_parity_check()
    assert h == (
        (0, 0, 0, 1, 1, 1, 1),
        (0, 1, 1, 0, 0, 1, 1),
        (1, 0, 1, 0, 1, 0, 1),
    )
    for j in range(1, 8):
        column = tuple(row[j - 1] for row in h)
        assert column == tuple(int(b) for b in format(j, "03b"))


def test_shape_is_three_by_seven():
    h = hamming_parity_check()
    assert len(h) == 3 and all(len(row) == 7 for row in h)


def test_the_appendix_d_syndrome_names_position_five():
    """Appendix D: s = (1, 0, 1) reads as 5, so e has its 1 in coordinate 5."""
    assert decode_hamming_syndrome((1, 0, 1)) == (0, 0, 0, 0, 1, 0, 0)


def test_that_error_really_produces_that_syndrome():
    """The decode is only right if H e^T comes back to (1, 0, 1)."""
    error = decode_hamming_syndrome((1, 0, 1))
    assert syndrome(hamming_parity_check(), error) == (1, 0, 1)


def test_every_single_bit_error_round_trips():
    """For each position, the syndrome names it and the decode recovers it."""
    h = hamming_parity_check()
    for position in range(1, 8):
        error = tuple(1 if i == position - 1 else 0 for i in range(7))
        s = syndrome(h, error)
        assert s == tuple(int(b) for b in format(position, "03b"))
        assert decode_hamming_syndrome(s) == error


def test_zero_syndrome_means_no_error():
    assert decode_hamming_syndrome((0, 0, 0)) == (0,) * 7


def test_a_codeword_has_zero_syndrome():
    """Any vector in the kernel of H is a codeword, so decoding finds no error."""
    h = hamming_parity_check()
    # Columns 3, 5, 6 are binary 011, 101, 110, which XOR to 000.
    codeword = (0, 0, 1, 0, 1, 1, 0)
    assert syndrome(h, codeword) == (0, 0, 0)
    assert decode_hamming_syndrome(syndrome(h, codeword)) == (0,) * 7


def test_the_construction_generalizes_beyond_three_bits():
    """bits = 4 gives the [15, 11] code, same column-order trick."""
    h = hamming_parity_check(bits=4)
    assert len(h) == 4 and all(len(row) == 15 for row in h)
    for position in range(1, 16):
        error = tuple(1 if i == position - 1 else 0 for i in range(15))
        assert decode_hamming_syndrome(syndrome(h, error), bits=4) == error
