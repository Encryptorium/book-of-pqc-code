"""The [7, 4] Hamming code Chapter 3's second exercise decodes.

The parity-check matrix here is the one whose `j`-th column is the binary
representation of `j`, most significant bit first, for `j = 1 .. 7`. That column
order is the whole trick: a weight-1 error at position `j` produces a syndrome
that spells `j` in binary, so decoding is a base-2 read rather than a search.

Chapter 3 uses this to draw the contrast the syndrome decoding problem rests on.
Decoding is easy here because the code has structure that the decoder knows;
scramble the columns and the same syndrome carries the same information but no
longer names the position, so recovering it needs a lookup table or a general
algorithm. The hardness in SDP is about *random* codes, not about decoding.

Standard library only.
"""

from __future__ import annotations

Matrix = tuple[tuple[int, ...], ...]


def hamming_parity_check(bits: int = 3) -> Matrix:
    """The parity-check matrix of the [2^bits - 1, 2^bits - 1 - bits] Hamming code.

    Returned as `bits` rows of `2^bits - 1` columns, with column `j - 1` holding
    the binary representation of `j` most significant bit first. `bits = 3` gives
    the [7, 4] code the chapter uses.
    """
    # EXERCISE: implement this function.
    #
    # Build bits rows of 2**bits - 1 columns, where column j - 1 holds the
    # binary representation of j with the most significant bit in row 0.
    # Extract bit row of j with (j >> (bits - 1 - row)) & 1. This column
    # order is the entire reason the decode in the next function is a read
    # rather than a search, so getting the bit order right is the exercise.
    #
    # Reference: Chapter 3, exercise 2
    #
    # Proved by:
    #   tests/ch03/test_codes.py
    raise NotImplementedError("exercise: hamming_parity_check")


def syndrome(matrix: Matrix, vector: tuple[int, ...]) -> tuple[int, ...]:
    """The syndrome `H e^T` over `F_2`, as a tuple of one bit per row of `H`."""
    # EXERCISE: implement this function.
    #
    # The matrix-vector product H e^T over F_2: one output bit per row, each
    # the sum of the products of that row against the vector, taken mod 2.
    # Addition in F_2 is XOR, so summing and reducing mod 2 is the same
    # thing as XOR-ing the selected columns.
    #
    # Reference: Chapter 3, 'Code problems: syndrome decoding of a random linear code'
    #
    # Proved by:
    #   tests/ch03/test_codes.py
    raise NotImplementedError("exercise: syndrome")


def decode_hamming_syndrome(
    syndrome_bits: tuple[int, ...], bits: int = 3
) -> tuple[int, ...]:
    """The weight-1 error vector whose syndrome is `syndrome_bits`.

    Reads the syndrome as a binary integer, most significant bit first. That
    integer *is* the 1-based error position, because column `j` of the matrix is
    the binary representation of `j`. A zero syndrome names no position and
    yields the all-zero vector, which is the correct answer for an uncorrupted
    codeword rather than a special case.
    """
    # EXERCISE: implement this function.
    #
    # Read the syndrome bits as a binary integer, most significant bit
    # first. That integer is the 1-based error position, because column j of
    # the matrix is the binary representation of j. Return a vector with a
    # single 1 in that coordinate. A zero syndrome names no position, so
    # return the all-zero vector: that is the correct answer for an
    # uncorrupted codeword rather than an error case to guard.
    #
    # Reference: Chapter 3, exercise 2
    #
    # Proved by:
    #   tests/ch03/test_codes.py
    raise NotImplementedError("exercise: decode_hamming_syndrome")
