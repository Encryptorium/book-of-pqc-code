"""Tests for GF(2) matrix arithmetic."""

from coding_theory.gf2 import mat_mul, mat_vec_mul, transpose, identity, weight, vec_add
from coding_theory.hamming import generator_matrix, parity_check_matrix


def test_identity_mul():
    """A * I = A for a 3-by-3 matrix."""
    A = [[1, 0, 1], [0, 1, 1], [1, 1, 0]]
    I = identity(3)
    assert mat_mul(A, I) == A


def test_h_times_g_transpose_is_zero():
    """The defining relationship: H * G^T = 0 over GF(2)."""
    H = parity_check_matrix()
    G = generator_matrix()
    Gt = transpose(G)
    product = mat_mul(H, Gt)
    zero = [[0] * len(G) for _ in range(len(H))]
    assert product == zero


def test_weight():
    """Hamming weight counts nonzero entries."""
    assert weight([0, 0, 0, 0]) == 0
    assert weight([1, 0, 1, 0]) == 2
    assert weight([1, 1, 1, 1, 1, 1, 1]) == 7


def test_vec_add():
    """Componentwise XOR."""
    assert vec_add([1, 0, 1], [0, 1, 1]) == [1, 1, 0]
    assert vec_add([1, 1, 1], [1, 1, 1]) == [0, 0, 0]


def test_transpose_roundtrip():
    """Transposing twice returns the original matrix."""
    A = [[1, 0], [0, 1], [1, 1]]
    assert transpose(transpose(A)) == A


def test_mat_vec_mul():
    """H * e for a single-bit error gives the column of H."""
    H = parity_check_matrix()
    for j in range(7):
        e = [0] * 7
        e[j] = 1
        result = mat_vec_mul(H, e)
        expected = [H[r][j] for r in range(3)]
        assert result == expected
