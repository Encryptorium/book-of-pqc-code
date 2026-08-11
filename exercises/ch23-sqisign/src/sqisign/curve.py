"""Elliptic curve arithmetic over F_{p^2} for short Weierstrass curves.

Curves have the form ``y^2 = x^3 + a*x + b`` where ``a`` and ``b``
are elements of F_{p^2}.  Points are represented as ``(x, y)`` tuples
of F_{p^2} elements, with ``None`` for the point at infinity.

Adapted from the Chapter 22 isogenies package.
"""

from __future__ import annotations

from typing import Optional

from sqisign.fp2 import (
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
    if pt is None:
        return True
    x, y = pt
    lhs = fp2_sqr(y, p)
    rhs = fp2_add(
        fp2_add(fp2_mul(fp2_sqr(x, p), x, p), fp2_mul(a, x, p), p),
        b,
        p,
    )
    return fp2_eq(lhs, rhs, p)


def point_neg(pt: Point, p: int) -> Point:
    if pt is None:
        return None
    x, y = pt
    return (x, fp2_neg(y, p))


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
    if k < 0:
        k = -k
        pt = point_neg(pt, p)
    if k == 0 or pt is None:
        return None
    result: Point = None
    addend = pt
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result


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
    current = pt
    for i in range(1, max_order + 1):
        if current is None:
            return i
        current = point_add(current, pt, a, p)
    raise ValueError(f"order exceeds {max_order}")
