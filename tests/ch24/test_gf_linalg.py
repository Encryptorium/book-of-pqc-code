"""GF(q) arithmetic and Gaussian elimination over a prime field."""

import pytest

from multivariate.gf import inv, matmul, transpose, mat_vec, quadratic_eval
from multivariate.linalg import is_invertible, invert_mat, solve_linear


Q = 7


def test_inverse_of_every_nonzero_element():
    """Fermat inversion returns a genuine inverse for all of GF(7)*."""
    for x in range(1, Q):
        assert x * inv(x, Q) % Q == 1


def test_zero_has_no_inverse():
    with pytest.raises(ZeroDivisionError):
        inv(0, Q)


def test_matmul_against_identity():
    identity = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
    A = [[1, 2, 3], [4, 5, 6], [0, 1, 2]]
    assert matmul(A, identity, Q) == [[x % Q for x in row] for row in A]
    assert matmul(identity, A, Q) == [[x % Q for x in row] for row in A]


def test_transpose_is_an_involution():
    A = [[1, 2, 3], [4, 5, 6]]
    assert transpose(transpose(A)) == A
    assert transpose(A) == [[1, 4], [2, 5], [3, 6]]


def test_mat_vec_matches_matmul_on_a_column():
    A = [[3, 1, 4], [1, 5, 9], [2, 6, 5]]
    v = [2, 3, 1]
    column = [[x] for x in v]
    assert mat_vec(A, v, Q) == [row[0] for row in matmul(A, column, Q)]


def test_quadratic_eval_matches_the_explicit_sum():
    Mat = [[1, 2], [3, 4]]
    x = [5, 6]
    expected = (1 * 5 * 5 + 2 * 5 * 6 + 3 * 6 * 5 + 4 * 6 * 6) % Q
    assert quadratic_eval(Mat, x, Q) == expected


def test_quadratic_eval_is_not_symmetrized():
    """An asymmetric matrix keeps both off-diagonal contributions."""
    Mat = [[0, 1], [0, 0]]
    assert quadratic_eval(Mat, [1, 1], Q) == 1


def test_singular_matrix_is_detected():
    singular = [[1, 2], [2, 4]]
    assert is_invertible(singular, Q) is False


def test_invertible_matrix_is_detected():
    A = [[1, 2], [3, 4]]
    assert is_invertible(A, Q) is True


def test_inverse_round_trip():
    A = [[1, 2, 0], [3, 4, 1], [0, 1, 5]]
    assert is_invertible(A, Q)
    A_inv = invert_mat(A, Q)
    product = matmul(A, A_inv, Q)
    assert product == [[1 if i == j else 0 for j in range(3)] for i in range(3)]


def test_solve_linear_recovers_a_known_solution():
    A = [[2, 1], [1, 3]]
    x = [4, 5]
    b = mat_vec(A, x, Q)
    assert solve_linear(A, b, Q) == x


def test_solve_linear_returns_none_when_singular():
    assert solve_linear([[1, 2], [2, 4]], [1, 1], Q) is None
