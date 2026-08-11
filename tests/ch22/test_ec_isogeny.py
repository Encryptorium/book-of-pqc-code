"""Tests for elliptic curve arithmetic over F_{p^2} (isogenies.curve)."""

from isogenies.fp2 import fp2_eq, fp2_scalar, fp2_sqrt, fp2_sqr, fp2_add, fp2_mul, fp2_zero
from isogenies.curve import (
    INF,
    is_on_curve,
    j_invariant,
    point_add,
    point_neg,
    point_order,
    scalar_mul,
)

P = 431
A = (1, 0)  # curve coefficient a = 1
B = (0, 0)  # curve coefficient b = 0

# Known F_p point on E_0: y^2 = x^3 + x
# x=2: rhs = 8+2 = 10. 10 is QR mod 431? Check.
# We'll use the generator found earlier: (13, 290) has order 432.
GEN = ((13, 0), (290, 0))


class TestPointOnCurve:
    def test_infinity_is_on_curve(self):
        assert is_on_curve(INF, A, B, P)

    def test_known_fp_point(self):
        assert is_on_curve(GEN, A, B, P)

    def test_two_torsion_point(self):
        T = ((0, 0), (0, 0))
        assert is_on_curve(T, A, B, P)

    def test_random_point_off_curve(self):
        bad = ((1, 0), (1, 0))  # y^2=1, x^3+x=2, 1!=2
        assert not is_on_curve(bad, A, B, P)

    def test_fp2_point(self):
        # x = (1, 4), compute rhs = x^3 + x in F_{p^2}
        x = (1, 4)
        x2 = fp2_sqr(x, P)
        x3 = fp2_mul(x2, x, P)
        rhs = fp2_add(x3, x, P)
        y = fp2_sqrt(rhs, P)
        assert y is not None
        pt = (x, y)
        assert is_on_curve(pt, A, B, P)


class TestPointAddition:
    def test_add_identity_left(self):
        R = point_add(INF, GEN, A, P)
        assert R is not None
        assert fp2_eq(R[0], GEN[0], P) and fp2_eq(R[1], GEN[1], P)

    def test_add_identity_right(self):
        R = point_add(GEN, INF, A, P)
        assert R is not None
        assert fp2_eq(R[0], GEN[0], P) and fp2_eq(R[1], GEN[1], P)

    def test_add_inverse_gives_infinity(self):
        neg_G = point_neg(GEN, P)
        assert point_add(GEN, neg_G, A, P) is None

    def test_doubling_via_add_vs_scalar_mul(self):
        double_add = point_add(GEN, GEN, A, P)
        double_scalar = scalar_mul(2, GEN, A, P)
        assert double_add is not None and double_scalar is not None
        assert fp2_eq(double_add[0], double_scalar[0], P)
        assert fp2_eq(double_add[1], double_scalar[1], P)


class TestScalarMul:
    def test_group_order(self):
        # #E_0(F_p) = 432, so 432*G = O for any F_p point G
        assert scalar_mul(432, GEN, A, P) is None

    def test_generator_order(self):
        assert point_order(GEN, A, P, 432) == 432

    def test_zero_scalar(self):
        assert scalar_mul(0, GEN, A, P) is None

    def test_one_scalar(self):
        R = scalar_mul(1, GEN, A, P)
        assert R is not None
        assert fp2_eq(R[0], GEN[0], P) and fp2_eq(R[1], GEN[1], P)


class TestJInvariant:
    def test_j_of_e0(self):
        # E_0: y^2 = x^3 + x has a=1, b=0
        # j = 1728 * 4*1^3 / (4*1^3 + 27*0^2) = 1728 * 4 / 4 = 1728
        j = j_invariant(A, B, P)
        expected = (1728 % P, 0)
        assert fp2_eq(j, expected, P)
