"""Tests for the Deuring correspondence at p = 431, E_0: y^2 = x^3 + x."""

from sqisign.fp2 import fp2_eq, fp2_pow, fp2_mul, fp2_neg
from sqisign.curve import (
    Point,
    is_on_curve,
    point_add,
    point_neg,
    scalar_mul,
)
from sqisign.deuring import (
    A0,
    B0,
    endo_id,
    endo_iota,
    endo_pi,
    endo_iota_pi,
    verify_iota_squared_is_neg_one,
    verify_iota_pi_anticommutes,
    quaternion_to_endo_action,
)


P = 431

# Sample F_p-rational points on E_0: y^2 = x^3 + x.
# A generator of E_0(F_p) of order 432 (from Ch 22 fixtures).
G_FP = ((13, 0), (290, 0))

# An F_{p^2}-rational point not in E_0(F_p): use Ch 22's PB image basis.
G_FP2 = ((128, 133), (47, 6))


def test_endomorphisms_land_on_curve():
    """All four endomorphisms map E_0 points to E_0 points."""
    for P_test in (G_FP, G_FP2):
        assert is_on_curve(endo_id(P_test), A0, B0, P)
        assert is_on_curve(endo_iota(P_test, P), A0, B0, P)
        assert is_on_curve(endo_pi(P_test, P), A0, B0, P)
        assert is_on_curve(endo_iota_pi(P_test, P), A0, B0, P)


def test_iota_squared_is_negation_on_F_p_points():
    """iota^2 = [-1] verified on F_p-rational points."""
    assert verify_iota_squared_is_neg_one(G_FP, P)


def test_iota_squared_is_negation_on_F_p2_points():
    """iota^2 = [-1] verified on F_{p^2}-rational points."""
    assert verify_iota_squared_is_neg_one(G_FP2, P)


def test_iota_pi_anticommutes_F_p():
    """iota*pi = -pi*iota on F_p-rational points."""
    assert verify_iota_pi_anticommutes(G_FP, P)


def test_iota_pi_anticommutes_F_p2():
    """iota*pi = -pi*iota on F_{p^2}-rational points."""
    assert verify_iota_pi_anticommutes(G_FP2, P)


def test_pi_fixes_F_p_points():
    """Frobenius is the identity on F_p-rational points."""
    image = endo_pi(G_FP, P)
    assert image is not None
    assert fp2_eq(image[0], G_FP[0], P)
    assert fp2_eq(image[1], G_FP[1], P)


def test_pi_squared_is_identity_on_F_p2_points():
    """pi^2 acts as identity on F_{p^2}-rational points (since x^{p^2} = x).

    This is NOT the same as pi^2 = [-p] in End(E_0).  The relation
    pi^2 = [-p] is the characteristic polynomial of Frobenius for a
    supersingular curve with trace 0 (Silverman 2009, V.2.3.1) and
    holds over the algebraic closure.  On F_{p^2}-rational points,
    [-p] does not in general equal [1].
    """
    pi_squared = endo_pi(endo_pi(G_FP2, P), P)
    assert pi_squared is not None
    assert fp2_eq(pi_squared[0], G_FP2[0], P)
    assert fp2_eq(pi_squared[1], G_FP2[1], P)


def test_endo_addition_via_curve():
    """Endomorphisms compose with curve addition: (id + iota)(P) = P + iota(P)."""
    sum_endo = quaternion_to_endo_action((1, 1, 0, 0), G_FP, P)
    direct = point_add(G_FP, endo_iota(G_FP, P), A0, P)
    assert sum_endo is not None
    assert direct is not None
    assert fp2_eq(sum_endo[0], direct[0], P)
    assert fp2_eq(sum_endo[1], direct[1], P)


def test_quaternion_action_negation():
    """The endomorphism [-1] = -id maps P to -P."""
    image = quaternion_to_endo_action((-1, 0, 0, 0), G_FP2, P)
    expected = point_neg(G_FP2, P)
    assert image is not None
    assert expected is not None
    assert fp2_eq(image[0], expected[0], P)
    assert fp2_eq(image[1], expected[1], P)


def test_quaternion_action_iota_squared_is_minus_one():
    """The endomorphism iota^2 = [-1]: as a (Z + Z*iota)-element, this
    means evaluating (0, 1, 0, 0) twice equals (-1, 0, 0, 0)."""
    once = quaternion_to_endo_action((0, 1, 0, 0), G_FP2, P)
    twice = quaternion_to_endo_action((0, 1, 0, 0), once, P)
    expected = quaternion_to_endo_action((-1, 0, 0, 0), G_FP2, P)
    assert twice is not None
    assert expected is not None
    assert fp2_eq(twice[0], expected[0], P)
    assert fp2_eq(twice[1], expected[1], P)
