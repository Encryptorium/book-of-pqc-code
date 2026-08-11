"""Tests for GF(2)[x]/(x^n - 1) polynomial arithmetic."""

from hqc.poly_gf2 import poly_add, poly_mul, poly_weight


N = 83


def test_poly_add_identity():
    a = [1, 0, 1, 0, 0] + [0] * (N - 5)
    zero = [0] * N
    assert poly_add(a, zero) == a


def test_poly_add_self_cancels():
    a = [1, 0, 1, 1, 0, 0, 1] + [0] * (N - 7)
    assert poly_add(a, a) == [0] * N


def test_poly_mul_identity():
    a = [1, 0, 1, 0, 0] + [0] * (N - 5)
    one = [1] + [0] * (N - 1)
    assert poly_mul(a, one, N) == a


def test_poly_mul_commutative():
    a = [1, 1, 0] + [0] * (N - 3)   # 1 + x
    b = [1, 0, 1] + [0] * (N - 3)   # 1 + x^2
    assert poly_mul(a, b, N) == poly_mul(b, a, N)


def test_poly_mul_known_product():
    # (1 + x) * (1 + x) = 1 + 2x + x^2 = 1 + x^2  over GF(2)
    a = [1, 1] + [0] * (N - 2)
    expected = [1, 0, 1] + [0] * (N - 3)
    assert poly_mul(a, a, N) == expected


def test_poly_mul_wraparound():
    # x^{n-1} * x = x^n mod (x^n - 1) = 1  over GF(2)
    a = [0] * (N - 1) + [1]   # x^{n-1}
    b = [0, 1] + [0] * (N - 2)  # x
    result = poly_mul(a, b, N)
    expected = [1] + [0] * (N - 1)   # 1
    assert result == expected


def test_poly_weight():
    a = [1, 0, 1, 0, 1] + [0] * (N - 5)
    assert poly_weight(a) == 3


def test_poly_weight_zero():
    assert poly_weight([0] * N) == 0
