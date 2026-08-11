"""Tests for quaternion algebra B_{p,inf} arithmetic at p = 431."""

from fractions import Fraction

from sqisign.quaternion import (
    Quat,
    quat,
    quat_zero,
    quat_one,
    quat_i,
    quat_j,
    quat_k,
    quat_add,
    quat_sub,
    quat_mul,
    quat_neg,
    quat_conj,
    quat_norm,
    quat_trace,
    quat_inv,
    quat_eq,
    quat_scalar,
)


P = 431


def test_basis_squares():
    """i^2 = -1, j^2 = -p, k^2 = -p in B_{p,inf}."""
    i = quat_i()
    j = quat_j()
    k = quat_k()

    assert quat_mul(i, i, P) == quat(-1, 0, 0, 0)
    assert quat_mul(j, j, P) == quat(-P, 0, 0, 0)
    assert quat_mul(k, k, P) == quat(-P, 0, 0, 0)


def test_anticommutation_relations():
    """ij = k, ji = -k, ik = -j, ki = j, jk = pi, kj = -pi."""
    i = quat_i()
    j = quat_j()
    k = quat_k()

    assert quat_mul(i, j, P) == k
    assert quat_mul(j, i, P) == quat_neg(k)
    assert quat_mul(i, k, P) == quat_neg(j)
    assert quat_mul(k, i, P) == j
    assert quat_mul(j, k, P) == quat(0, P, 0, 0)
    assert quat_mul(k, j, P) == quat(0, -P, 0, 0)


def test_associativity():
    """Multiplication is associative on a sample triple."""
    x = quat(2, 3, 1, 5)
    y = quat(1, -1, 4, 2)
    z = quat(3, 0, 2, -1)

    left = quat_mul(quat_mul(x, y, P), z, P)
    right = quat_mul(x, quat_mul(y, z, P), P)
    assert left == right


def test_non_commutative():
    """The algebra is non-commutative: ij != ji for at least one pair."""
    i = quat_i()
    j = quat_j()
    assert quat_mul(i, j, P) != quat_mul(j, i, P)


def test_norm_formula():
    """nrd(a + bi + cj + dk) = a^2 + b^2 + p*c^2 + p*d^2."""
    x = quat(2, 3, 1, 5)
    expected = Fraction(4 + 9 + P * 1 + P * 25)
    assert quat_norm(x, P) == expected


def test_norm_multiplicative():
    """nrd(x*y) = nrd(x) * nrd(y)."""
    x = quat(2, 3, 1, 5)
    y = quat(1, -1, 4, 2)
    nx = quat_norm(x, P)
    ny = quat_norm(y, P)
    nxy = quat_norm(quat_mul(x, y, P), P)
    assert nxy == nx * ny


def test_conj_involution():
    """conj(conj(x)) = x for any quaternion."""
    x = quat(2, 3, 1, 5)
    assert quat_conj(quat_conj(x)) == x


def test_conj_anti_homomorphism():
    """conj(x*y) = conj(y) * conj(x)."""
    x = quat(2, 3, 1, 5)
    y = quat(1, -1, 4, 2)
    lhs = quat_conj(quat_mul(x, y, P))
    rhs = quat_mul(quat_conj(y), quat_conj(x), P)
    assert lhs == rhs


def test_norm_via_conj():
    """x * conj(x) is a scalar quaternion equal to (nrd(x), 0, 0, 0)."""
    x = quat(2, 3, 1, 5)
    n = quat_norm(x, P)
    product = quat_mul(x, quat_conj(x), P)
    assert product == (n, Fraction(0), Fraction(0), Fraction(0))


def test_trace_formula():
    """trd(x) = 2*a for x = a + bi + cj + dk."""
    x = quat(2, 3, 1, 5)
    assert quat_trace(x) == 4


def test_inverse():
    """x * x^{-1} = 1."""
    x = quat(2, 3, 1, 5)
    inv = quat_inv(x, P)
    product = quat_mul(x, inv, P)
    assert product == quat_one()


def test_unit_norm_one():
    """nrd(1) = 1, nrd(i) = 1, nrd(j) = p, nrd(k) = p."""
    assert quat_norm(quat_one(), P) == 1
    assert quat_norm(quat_i(), P) == 1
    assert quat_norm(quat_j(), P) == P
    assert quat_norm(quat_k(), P) == P
