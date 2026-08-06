"""Tests for is_unimodular and change_of_basis."""

import numpy as np
import pytest

from lattices import Lattice, is_unimodular, change_of_basis


def test_identity_is_unimodular():
    assert is_unimodular(np.eye(4, dtype=np.int64))


def test_upper_triangular_unimodular():
    U = np.array([[1, 2, 3], [0, 1, -4], [0, 0, 1]], dtype=np.int64)
    assert is_unimodular(U)


def test_scaling_is_not_unimodular():
    assert not is_unimodular(2 * np.eye(3, dtype=np.int64))


def test_non_integer_not_unimodular():
    assert not is_unimodular(np.array([[1.5, 0.0], [0.0, 1.0]]))


def test_change_of_basis_detects_equivalent_bases():
    B1 = np.array([[2, 5], [7, 3]], dtype=np.int64)
    U = np.array([[1, 3], [0, 1]], dtype=np.int64)
    B2 = B1 @ U
    recovered = change_of_basis(B1, B2)
    assert recovered is not None
    assert np.array_equal(recovered, U)


def test_change_of_basis_rejects_non_equivalent():
    B1 = np.array([[1, 0], [0, 1]], dtype=np.int64)
    B2 = 2 * B1  # 2Z^2 is a strict sublattice of Z^2
    assert change_of_basis(B1, B2) is None


def test_change_of_basis_roundtrip():
    B1 = np.array([[3, 1], [2, 5]], dtype=np.int64)
    U = np.array([[2, 1], [1, 1]], dtype=np.int64)  # det = 1
    B2 = B1 @ U
    recovered = change_of_basis(B1, B2)
    assert recovered is not None
    # B1 @ recovered should equal B2.
    assert np.array_equal((B1 @ recovered), B2)


def test_change_of_basis_raises_on_singular_first_basis():
    B1_singular = np.array([[1, 2], [2, 4]], dtype=float)
    B2 = np.eye(2, dtype=float)
    with pytest.raises(np.linalg.LinAlgError):
        change_of_basis(B1_singular, B2)


def test_equivalent_bases_generate_same_lattice_points():
    """The basis-equivalence theorem at the membership level.

    If B2 = B1 @ U for a unimodular U, then every lattice point
    produced by L(B1) is contained in L(B2) and vice versa. This is
    the geometric statement of the theorem; the other tests only
    check the algebraic identity B2 = B1 @ U.
    """
    B1 = np.array([[3, 1], [1, 2]], dtype=np.int64)
    U = np.array([[1, 1], [0, 1]], dtype=np.int64)
    B2 = B1 @ U
    L1 = Lattice(basis=B1)
    L2 = Lattice(basis=B2)

    # Generate several lattice points from L1 by enumerating small
    # integer coefficient tuples, then verify L2 also contains them.
    for i in range(-2, 3):
        for j in range(-2, 3):
            p1 = L1.point([i, j])
            assert L2.contains(p1)
            p2 = L2.point([i, j])
            assert L1.contains(p2)
