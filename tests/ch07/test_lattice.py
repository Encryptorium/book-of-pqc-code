"""Tests for the Lattice class."""

import numpy as np
import pytest

from lattices import Lattice


def test_standard_basis_z2():
    L = Lattice(basis=np.eye(2, dtype=np.int64))
    assert L.dimension == 2
    assert np.array_equal(L.point([3, -2]), np.array([3, -2]))


def test_nontrivial_basis_z2():
    B = np.array([[2, 5], [7, 3]], dtype=np.int64)
    L = Lattice(basis=B)
    assert L.dimension == 2
    assert np.array_equal(L.point([1, 1]), np.array([7, 10]))
    assert np.array_equal(L.point([1, -1]), np.array([-3, 4]))


def test_contains_true_for_integer_combination():
    B = np.array([[2, 5], [7, 3]], dtype=np.int64)
    L = Lattice(basis=B)
    v = L.point([2, -3])
    assert L.contains(v)


def test_contains_false_for_non_lattice_point():
    L = Lattice(basis=np.array([[2, 5], [7, 3]], dtype=np.int64))
    assert not L.contains([1, 1])


def test_rejects_non_square_basis():
    with pytest.raises(AssertionError):
        Lattice(basis=np.array([[1, 0, 0], [0, 1, 0]], dtype=np.int64))


def test_rejects_non_integer_basis():
    with pytest.raises(AssertionError):
        Lattice(basis=np.array([[1.5, 0.0], [0.0, 1.0]]))


def test_rejects_singular_basis():
    with pytest.raises(AssertionError):
        Lattice(basis=np.array([[1, 2], [2, 4]], dtype=np.int64))
