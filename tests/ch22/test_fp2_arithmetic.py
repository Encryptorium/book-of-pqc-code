"""Tests for F_{p^2} arithmetic (isogenies.fp2)."""

import pytest

from isogenies.fp2 import (
    fp2_add,
    fp2_eq,
    fp2_int_mul,
    fp2_inv,
    fp2_is_square,
    fp2_mul,
    fp2_neg,
    fp2_one,
    fp2_pow,
    fp2_scalar,
    fp2_sqr,
    fp2_sqrt,
    fp2_sub,
    fp2_zero,
)

P = 431


class TestBasicOps:
    def test_add_sub_inverse(self):
        x = (100, 200)
        y = (300, 150)
        s = fp2_add(x, y, P)
        assert fp2_eq(fp2_sub(s, y, P), x, P)

    def test_neg_is_additive_inverse(self):
        x = (17, 42)
        assert fp2_eq(fp2_add(x, fp2_neg(x, P), P), fp2_zero(), P)

    def test_mul_commutativity(self):
        x = (7, 13)
        y = (100, 200)
        assert fp2_eq(fp2_mul(x, y, P), fp2_mul(y, x, P), P)

    def test_mul_associativity(self):
        x = (3, 5)
        y = (7, 11)
        z = (13, 17)
        lhs = fp2_mul(fp2_mul(x, y, P), z, P)
        rhs = fp2_mul(x, fp2_mul(y, z, P), P)
        assert fp2_eq(lhs, rhs, P)

    def test_i_squared_is_minus_one(self):
        i = (0, 1)
        i_sq = fp2_mul(i, i, P)
        assert fp2_eq(i_sq, (P - 1, 0), P)

    def test_sqr_matches_mul(self):
        x = (42, 99)
        assert fp2_eq(fp2_sqr(x, P), fp2_mul(x, x, P), P)


class TestInversion:
    def test_inv_roundtrip(self):
        x = (17, 42)
        assert fp2_eq(fp2_mul(x, fp2_inv(x, P), P), fp2_one(), P)

    def test_inv_of_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            fp2_inv(fp2_zero(), P)

    def test_inv_of_scalar(self):
        x = fp2_scalar(7, P)
        x_inv = fp2_inv(x, P)
        assert fp2_eq(fp2_mul(x, x_inv, P), fp2_one(), P)


class TestPow:
    def test_pow_zero(self):
        x = (3, 5)
        assert fp2_eq(fp2_pow(x, 0, P), fp2_one(), P)

    def test_pow_one(self):
        x = (3, 5)
        assert fp2_eq(fp2_pow(x, 1, P), x, P)

    def test_pow_matches_repeated_mul(self):
        x = (7, 11)
        manual = fp2_one()
        for _ in range(5):
            manual = fp2_mul(manual, x, P)
        assert fp2_eq(fp2_pow(x, 5, P), manual, P)

    def test_fermats_little_theorem(self):
        x = (17, 42)
        # x^{p^2 - 1} = 1 for nonzero x
        assert fp2_eq(fp2_pow(x, P * P - 1, P), fp2_one(), P)


class TestSqrt:
    def test_sqrt_of_zero(self):
        assert fp2_sqrt(fp2_zero(), P) == fp2_zero()

    def test_sqrt_of_square(self):
        x = (17, 42)
        x_sq = fp2_sqr(x, P)
        r = fp2_sqrt(x_sq, P)
        assert r is not None
        assert fp2_eq(fp2_sqr(r, P), x_sq, P)

    def test_sqrt_of_nonsquare_returns_none(self):
        # Find a non-square in F_{p^2}
        nr = (0, 1)
        for a in range(P):
            nr = (a, 1)
            if not fp2_is_square(nr, P):
                break
        assert fp2_sqrt(nr, P) is None

    def test_sqrt_of_fp_element(self):
        # 2 is a QR mod 431
        z = fp2_scalar(2, P)
        r = fp2_sqrt(z, P)
        assert r is not None
        assert fp2_eq(fp2_sqr(r, P), z, P)
