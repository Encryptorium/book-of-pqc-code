"""Elliptic curve arithmetic over F_{p^2} for short Weierstrass curves.

Curves have the form ``y^2 = x^3 + a*x + b`` where ``a`` and ``b``
are elements of F_{p^2}.  Points are represented as ``(x, y)`` tuples
of F_{p^2} elements, with ``None`` for the point at infinity.
"""

from __future__ import annotations

from typing import Optional

from isogenies.fp2 import (
    fp2_add,
    fp2_eq,
    fp2_inv,
    fp2_mul,
    fp2_neg,
    fp2_one,
    fp2_scalar,
    fp2_sqr,
    fp2_sub,
    fp2_int_mul,
    fp2_zero,
)

# A point is either None (infinity) or a tuple of two F_{p^2} elements.
Fp2 = tuple[int, int]
Point = Optional[tuple[Fp2, Fp2]]

INF: Point = None


def is_on_curve(
    pt: Point, a: Fp2, b: Fp2, p: int
) -> bool:
    # EXERCISE: implement this function.
    #
    # The point at infinity is represented as None and is on every curve, so
    # return True for it. Otherwise evaluate y^2 against x^3 + a*x + b with
    # F_p^2 operations throughout and compare with fp2_eq. Nothing else in
    # the package validates its inputs, so this is the check the tests use
    # to confirm that isogeny images really land on the codomain they claim.
    #
    # Reference: Chapter 22, 'Elliptic curve arithmetic over F_p^2'
    #
    # Proved by:
    #   tests/ch22/test_ec_isogeny.py
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: is_on_curve")


def point_neg(pt: Point, p: int) -> Point:
    # EXERCISE: implement this function.
    #
    # The group inverse: (x, y) goes to (x, -y), and None goes to None. It
    # is reflection across the x-axis. point_add's degenerate branch is
    # testing exactly this relation when it checks whether y1 equals the
    # negation of y2 and returns the identity.
    #
    # Reference: Chapter 22, 'Elliptic curve arithmetic over F_p^2'
    #
    # Proved by:
    #   tests/ch22/test_ec_isogeny.py
    raise NotImplementedError("exercise: point_neg")


def point_add(
    p1: Point, p2: Point, a: Fp2, p: int
) -> Point:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if fp2_eq(x1, x2, p):
        if fp2_eq(y1, fp2_neg(y2, p), p):
            return None
        # Doubling: lam = (3*x1^2 + a) / (2*y1)
        three = fp2_scalar(3, p)
        two = fp2_scalar(2, p)
        num = fp2_add(fp2_mul(three, fp2_sqr(x1, p), p), a, p)
        den = fp2_mul(two, y1, p)
        lam = fp2_mul(num, fp2_inv(den, p), p)
    else:
        # General addition: lam = (y2 - y1) / (x2 - x1)
        num = fp2_sub(y2, y1, p)
        den = fp2_sub(x2, x1, p)
        lam = fp2_mul(num, fp2_inv(den, p), p)
    # x3 = lam^2 - x1 - x2
    x3 = fp2_sub(fp2_sub(fp2_sqr(lam, p), x1, p), x2, p)
    # y3 = lam*(x1 - x3) - y1
    y3 = fp2_sub(fp2_mul(lam, fp2_sub(x1, x3, p), p), y1, p)
    return (x3, y3)


def scalar_mul(k: int, pt: Point, a: Fp2, p: int) -> Point:
    """Compute ``k * pt`` by left-to-right double-and-add."""
    # EXERCISE: implement this function.
    #
    # Double-and-add over the bits of k from the low end. Keep an
    # accumulator starting at the identity and an addend starting at pt;
    # when the current bit is set, add the addend into the accumulator, then
    # double the addend and shift k right by one. A negative k means
    # negating the point and using the absolute value. Return None when k is
    # zero or pt is already the identity. The chain walk leans on this to
    # scale a kernel generator of order l^m down to a point of order exactly
    # l.
    #
    # Reference: Chapter 22, 'Elliptic curve arithmetic over F_p^2'
    #
    # Proved by:
    #   tests/ch22/test_ec_isogeny.py
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: scalar_mul")


def j_invariant(a: Fp2, b: Fp2, p: int) -> Fp2:
    """Compute the j-invariant: j = 1728 * 4a^3 / (4a^3 + 27b^2)."""
    a3 = fp2_mul(fp2_sqr(a, p), a, p)
    four_a3 = fp2_int_mul(4, a3, p)
    b2 = fp2_sqr(b, p)
    twentyseven_b2 = fp2_int_mul(27, b2, p)
    denom = fp2_add(four_a3, twentyseven_b2, p)
    return fp2_mul(fp2_int_mul(1728, four_a3, p), fp2_inv(denom, p), p)


def point_order(pt: Point, a: Fp2, p: int, max_order: int) -> int:
    """Find the order of *pt* by brute force up to *max_order*."""
    # EXERCISE: implement this function.
    #
    # Brute force. Add pt into a running total and return i the first time
    # the total is the identity, with the count starting at 1 so that the
    # identity itself reports order 1. Raise ValueError once max_order is
    # passed rather than looping without bound: a point whose order exceeds
    # the caller's expectation is a broken fixture, not a slow computation.
    # The SIDH tests use this to confirm the four fixed torsion-basis points
    # have order 2^e_A and 3^e_B.
    #
    # Reference: Chapter 22, 'Elliptic curve arithmetic over F_p^2'
    #
    # Proved by:
    #   tests/ch22/test_ec_isogeny.py
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: point_order")
