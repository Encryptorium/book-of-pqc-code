"""Tests for the dual lattice.

The dual of a full-rank integer lattice L with basis B is the lattice
with basis B^{-T}. Two properties matter:

1. The defining inner-product condition: for every lattice vector x
   in L and every dual lattice vector y in L*, <y, x> is an integer.
2. Dual-of-dual: (B^{-T})^{-T} = B, so the dual of L* is L again.
"""

import numpy as np

from lattices import Lattice, dual_basis


def test_dual_of_standard_basis():
    B = np.eye(3, dtype=np.int64)
    D = dual_basis(B)
    # Z^n is self-dual: dual basis equals the original basis.
    assert np.allclose(D, B)


def test_dual_basis_inner_product_is_integer():
    B = np.array([[2, 5], [7, 3]], dtype=np.int64).astype(float)
    D = dual_basis(B)
    # For every pair of basis vectors b_i and d_j we should have
    # <d_j, b_i> in {0, 1}, specifically the Kronecker delta.
    inner = D.T @ B
    assert np.allclose(inner, np.eye(2))


def test_dual_of_dual_is_original():
    B = np.array([[2, 5], [7, 3]], dtype=np.int64).astype(float)
    D = dual_basis(B)
    DD = dual_basis(D)
    assert np.allclose(DD, B)


def test_dual_points_pair_to_integers():
    # Pick a lattice L with basis B and its dual L* with basis D.
    # Take a lattice point x = B @ k for some integer k and a dual
    # point y = D @ j for some integer j; then <y, x> must be integer.
    B = np.array([[3, 1], [2, 5]], dtype=np.int64).astype(float)
    D = dual_basis(B)

    rng_k = np.array([[2, -1, 3], [4, 0, -2]])
    rng_j = np.array([[1, 3, -1], [-2, 2, 0]])
    for i in range(3):
        x = B @ rng_k[:, i]
        y = D @ rng_j[:, i]
        inner = float(np.dot(y, x))
        assert abs(inner - round(inner)) < 1e-9
