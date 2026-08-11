"""Tests for the standard maximal order O_0 in B_{p,inf} at p = 431."""

from fractions import Fraction

import pytest

from sqisign.quaternion import (
    quat,
    quat_one,
    quat_i,
    quat_j,
    quat_k,
    quat_mul,
    quat_norm,
    quat_add,
    quat_scalar,
)
from sqisign.orders import (
    standard_basis,
    in_standard_order,
    order_coords,
    left_ideal_basis,
    ideal_norm_principal,
    is_in_lattice,
)


P = 431


def test_standard_basis_size():
    """O_0 has a Z-basis of size 4."""
    basis = standard_basis(P)
    assert len(basis) == 4


def test_basis_membership():
    """Every basis element of O_0 lies in O_0."""
    for b in standard_basis(P):
        assert in_standard_order(b, P)


def test_unit_in_order():
    """1, i, j, k all need scrutiny: 1 and i are in O_0, j and k are not directly."""
    assert in_standard_order(quat_one(), P)
    assert in_standard_order(quat_i(), P)
    # j = 2 * (1+j)/2 - 1, so j IS in O_0.
    assert in_standard_order(quat_j(), P)
    # k = 2 * (i+k)/2 - i, so k IS in O_0.
    assert in_standard_order(quat_k(), P)


def test_half_basis_not_in_order():
    """j/2 is not in O_0 (it would require c = 1/2 with a - c integer, but a = 0)."""
    half_j = quat(0, 0, Fraction(1, 2), 0)
    assert not in_standard_order(half_j, P)
    half_i = quat(0, Fraction(1, 2), 0, 0)
    assert not in_standard_order(half_i, P)


def test_order_closed_under_multiplication():
    """O_0 is a ring: products of basis elements lie in O_0."""
    basis = standard_basis(P)
    for x in basis:
        for y in basis:
            product = quat_mul(x, y, P)
            assert in_standard_order(product, P), f"{x} * {y} = {product} not in O_0"


def test_order_coords_roundtrip():
    """For x in O_0, expressing x in the O_0 basis and reconstructing yields x."""
    basis = standard_basis(P)
    x = quat(3, -2, 5, 1)  # 3 + 3i*0 + ... wait, this is 3 - 2i + 5j + k
    coords = order_coords(x, P)
    reconstructed = quat(0, 0, 0, 0)
    for c, b in zip(coords, basis):
        reconstructed = quat_add(reconstructed, quat_scalar(b, c))
    assert reconstructed == x


def test_order_coords_rejects_non_member():
    """order_coords raises ValueError for elements not in O_0."""
    half_j = quat(0, 0, Fraction(1, 2), 0)
    with pytest.raises(ValueError):
        order_coords(half_j, P)


def test_principal_ideal_norm():
    """For a principal left ideal O_0 * alpha, nrd(I) = nrd(alpha)."""
    alpha = quat(2, 1, 1, 0)  # nrd = 4 + 1 + 431 + 0 = 436
    n = ideal_norm_principal(alpha, P)
    assert n == quat_norm(alpha, P)
    assert n == 436


def test_left_ideal_basis_in_order():
    """The basis of O_0 * alpha consists of products beta * alpha for beta in O_0."""
    alpha = quat(2, 1, 0, 0)  # 2 + i
    basis = left_ideal_basis(alpha, P)
    assert len(basis) == 4
    # Each generator should be in O_0 * alpha (trivially, by construction).
    # Verify by checking that beta * alpha lies in the order when alpha is in O_0
    # (this is a sanity check that O_0 * alpha is a sublattice of O_0 when alpha in O_0).
    for b in basis:
        assert in_standard_order(b, P)


def test_lattice_membership():
    """is_in_lattice correctly identifies members of the O_0 lattice."""
    basis = standard_basis(P)
    # i + j is 1*0 + 0*i + ... let's pick something concrete
    x = quat_add(quat_i(), quat_j())  # i + j
    assert is_in_lattice(x, basis)
    # Half-element should not be in the lattice
    half_j = quat(0, 0, Fraction(1, 2), 0)
    assert not is_in_lattice(half_j, basis)


def test_order_basis_equals_membership_test():
    """is_in_lattice(x, standard_basis) agrees with in_standard_order(x)."""
    basis = standard_basis(P)
    samples = [
        quat(1, 0, 0, 0),
        quat(0, 1, 0, 0),
        quat(0, 0, 1, 0),
        quat(0, 0, 0, 1),
        quat(Fraction(1, 2), 0, Fraction(1, 2), 0),
        quat(0, Fraction(1, 2), 0, Fraction(1, 2)),
        quat(Fraction(1, 2), 0, 0, 0),  # not in O_0
        quat(0, 0, Fraction(1, 2), 0),  # not in O_0
    ]
    for x in samples:
        assert is_in_lattice(x, basis) == in_standard_order(x, P), f"mismatch for {x}"
