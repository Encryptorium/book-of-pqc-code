"""Tests for the q-ary lattice basis."""

import numpy as np

from lwe import qary_lattice_basis


def test_basis_has_correct_shape(toy):
    rng = np.random.default_rng(seed=0)
    A = rng.integers(low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64)
    B = qary_lattice_basis(A, toy.q)
    assert B.shape == (toy.m, toy.m)
    assert B.dtype == np.int64


def test_basis_rows_annihilate_A_transpose(toy):
    rng = np.random.default_rng(seed=1)
    A = rng.integers(low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64)
    B = qary_lattice_basis(A, toy.q)
    for i in range(toy.m):
        v = B[i]
        residual = (A.T @ v) % toy.q
        assert np.all(residual == 0), (
            f"row {i}: A^T @ v mod q = {residual.tolist()}, expected all zero"
        )


def test_determinant_equals_q_to_the_n(toy):
    rng = np.random.default_rng(seed=2)
    A = rng.integers(low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64)
    B = qary_lattice_basis(A, toy.q)
    det = int(round(np.linalg.det(B.astype(float))))
    assert abs(det) == toy.q ** toy.n, (
        f"|det B| = {abs(det)}, expected q^n = {toy.q ** toy.n}"
    )


def test_many_random_matrices_give_consistent_determinant(toy):
    for seed in range(10):
        rng = np.random.default_rng(seed=seed)
        A = rng.integers(
            low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64
        )
        B = qary_lattice_basis(A, toy.q)
        det = int(round(np.linalg.det(B.astype(float))))
        assert abs(det) == toy.q ** toy.n, (
            f"seed={seed}: |det B| = {abs(det)}, expected {toy.q ** toy.n}"
        )


def test_basis_vectors_are_linearly_independent_over_Q(toy):
    rng = np.random.default_rng(seed=3)
    A = rng.integers(low=0, high=toy.q, size=(toy.m, toy.n), dtype=np.int64)
    B = qary_lattice_basis(A, toy.q)
    rank = int(np.linalg.matrix_rank(B.astype(float)))
    assert rank == toy.m
