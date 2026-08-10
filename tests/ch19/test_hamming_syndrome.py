"""Tests for Hamming syndrome computation and syndrome table."""

from coding_theory.hamming import (
    parity_check_matrix,
    encode,
    syndrome,
    syndrome_table,
)


def test_syndrome_of_codeword_is_zero():
    """The syndrome of any valid codeword is the zero vector."""
    msg = [1, 0, 1, 1]
    cw = encode(msg)
    assert syndrome(cw) == [0, 0, 0]


def test_single_error_syndrome_is_column_of_h():
    """The syndrome of a single-bit error at position j is column j of H."""
    H = parity_check_matrix()
    cw = encode([0, 0, 0, 0])  # the all-zero codeword
    for j in range(7):
        received = list(cw)
        received[j] ^= 1
        s = syndrome(received)
        expected = [H[r][j] for r in range(3)]
        assert s == expected, f"error at pos {j}: got {s}, expected {expected}"


def test_syndrome_table_has_8_entries():
    """The syndrome table has 7 nonzero syndromes + the zero syndrome."""
    table = syndrome_table()
    assert len(table) == 8


def test_syndrome_table_zero_maps_to_no_error():
    """The zero syndrome maps to -1 (no error)."""
    table = syndrome_table()
    assert table[(0, 0, 0)] == -1


def test_syndrome_table_covers_all_positions():
    """Every position 0..6 appears exactly once in the nonzero syndromes."""
    table = syndrome_table()
    positions = sorted(v for v in table.values() if v >= 0)
    assert positions == list(range(7))
