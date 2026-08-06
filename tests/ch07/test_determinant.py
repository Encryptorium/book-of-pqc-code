"""Tests for the lattice determinant and its basis-invariance."""

import numpy as np

from lattices import Lattice, det, change_of_basis, is_unimodular


def test_det_standard_basis_z2():
    L = Lattice(basis=np.eye(2, dtype=np.int64))
    assert det(L) == 1


def test_det_standard_basis_z3():
    L = Lattice(basis=np.eye(3, dtype=np.int64))
    assert det(L) == 1


def test_det_small_2d_lattice():
    B = np.array([[2, 5], [7, 3]], dtype=np.int64)
    # |det B| = |2*3 - 5*7| = |6 - 35| = 29
    assert det(B) == 29


def test_det_invariant_under_unimodular_change():
    B1 = np.array([[2, 5], [7, 3]], dtype=np.int64)
    U = np.array([[1, 2], [0, 1]], dtype=np.int64)  # unimodular
    assert is_unimodular(U)
    B2 = B1 @ U
    assert det(B1) == det(B2) == 29


def test_det_changes_under_non_unimodular_scale():
    # Scaling by 2 is NOT unimodular; the sublattice 2L has determinant
    # 2^n * det(L).
    B = np.array([[2, 5], [7, 3]], dtype=np.int64)
    B_scaled = 2 * B
    assert det(B_scaled) == 4 * det(B)


def test_det_3d_triangular_lattice():
    B = np.array(
        [
            [3, 0, 0],
            [1, 5, 0],
            [2, 4, 7],
        ],
        dtype=np.int64,
    )
    # Triangular matrix: det = product of diagonal = 3 * 5 * 7 = 105
    assert det(B) == 105
