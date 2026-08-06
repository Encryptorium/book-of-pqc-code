"""Tests for Minkowski's bound.

For a full-rank lattice L in R^n, Minkowski's theorem gives
    lambda_1(L) <= sqrt(n) * det(L)^{1/n}.

This test suite checks, on small lattices where the shortest
vector can be found by brute force, that the actual shortest
vector's length is below the bound.
"""

import itertools
import math

import numpy as np

from lattices import Lattice, minkowski_bound


def _shortest_nonzero_vector_length(basis: np.ndarray, radius: int = 6) -> float:
    n = basis.shape[1]
    best = math.inf
    for coeffs in itertools.product(range(-radius, radius + 1), repeat=n):
        if all(c == 0 for c in coeffs):
            continue
        v = basis @ np.asarray(coeffs, dtype=np.int64)
        length = float(np.linalg.norm(v))
        if length < best:
            best = length
    return best


def test_bound_holds_on_standard_z2():
    L = Lattice(basis=np.eye(2, dtype=np.int64))
    bound = minkowski_bound(L)
    # sqrt(2) * 1^(1/2) = sqrt(2) ~= 1.414
    assert abs(bound - math.sqrt(2)) < 1e-9
    shortest = _shortest_nonzero_vector_length(L.basis)
    assert shortest <= bound + 1e-9


def test_bound_holds_on_ch3_2d_example():
    # Basis from Chapter 3's motivating example: (2, 7) and (5, 3).
    # Note: Ch 3 writes basis vectors as rows; here we put them as columns.
    B = np.array([[2, 5], [7, 3]], dtype=np.int64)
    L = Lattice(basis=B)
    bound = minkowski_bound(L)
    shortest = _shortest_nonzero_vector_length(L.basis)
    # A shortest vector of this lattice has length 5 (attained at +/-(3, -4)).
    assert abs(shortest - 5.0) < 1e-9
    assert shortest <= bound + 1e-9


def test_bound_holds_on_3d_triangular_lattice():
    B = np.array(
        [
            [3, 0, 0],
            [1, 5, 0],
            [2, 4, 7],
        ],
        dtype=np.int64,
    )
    L = Lattice(basis=B)
    bound = minkowski_bound(L)
    shortest = _shortest_nonzero_vector_length(L.basis, radius=3)
    assert shortest <= bound + 1e-9


def test_bound_formula_matches_definition():
    # Sanity check: for Z^n with n = 4, the bound is sqrt(4) * 1 = 2.
    L = Lattice(basis=np.eye(4, dtype=np.int64))
    assert abs(minkowski_bound(L) - 2.0) < 1e-9
