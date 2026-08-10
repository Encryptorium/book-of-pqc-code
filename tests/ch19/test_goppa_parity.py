"""Tests for the Goppa code parity-check matrix construction."""

from coding_theory.goppa import goppa_parity_check_gf8, _gf8_mul, _gf8_inv


def test_goppa_matrix_dimensions():
    """A t=1 Goppa code over GF(8) with 7-element support gives a 3x7 matrix."""
    H = goppa_parity_check_gf8(g_root=3, support=[0, 1, 2, 4, 5, 6, 7])
    assert len(H) == 3
    assert all(len(row) == 7 for row in H)


def test_goppa_columns_nonzero():
    """Every column of the Goppa parity-check matrix is nonzero."""
    H = goppa_parity_check_gf8(g_root=3, support=[0, 1, 2, 4, 5, 6, 7])
    for j in range(7):
        col = [H[r][j] for r in range(3)]
        assert col != [0, 0, 0], f"column {j} is zero"


def test_goppa_columns_binary():
    """All entries are 0 or 1."""
    H = goppa_parity_check_gf8(g_root=3, support=[0, 1, 2, 4, 5, 6, 7])
    for r in range(3):
        for c in range(7):
            assert H[r][c] in (0, 1)


def test_gf8_mul_identity():
    """Multiplying by 1 in GF(8) is the identity."""
    for a in range(8):
        assert _gf8_mul(a, 1) == a


def test_gf8_inv_roundtrip():
    """a * a^{-1} = 1 for all nonzero elements of GF(8)."""
    for a in range(1, 8):
        assert _gf8_mul(a, _gf8_inv(a)) == 1
