"""Arithmetic in the quaternion algebra B_{p,inf} ramified at p and infinity.

For any prime p, B_{p,inf} = Q + Q*i + Q*j + Q*k with multiplication rules:
    i^2 = -1,  j^2 = -p,  k = i*j = -j*i

So k^2 = (ij)(ij) = -i*j*j*i = -i*(-p)*i = p*i^2 = -p, and the algebra
is non-commutative since ij = -ji.

Elements are represented as 4-tuples ``(a, b, c, d)`` of ``Fraction``
objects, denoting ``alpha = a + b*i + c*j + d*k``.

Reference: Voight, "Quaternion Algebras", Springer GTM, 2021.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Union


# A quaternion element is a 4-tuple of Fractions.
Quat = tuple[Fraction, Fraction, Fraction, Fraction]


def _to_fraction(x: Union[int, Fraction]) -> Fraction:
    if isinstance(x, Fraction):
        return x
    return Fraction(x)


def quat(a: Union[int, Fraction], b: Union[int, Fraction],
         c: Union[int, Fraction], d: Union[int, Fraction]) -> Quat:
    """Construct a quaternion a + b*i + c*j + d*k."""
    return (_to_fraction(a), _to_fraction(b), _to_fraction(c), _to_fraction(d))


def quat_zero() -> Quat:
    return quat(0, 0, 0, 0)


def quat_one() -> Quat:
    return quat(1, 0, 0, 0)


def quat_i() -> Quat:
    return quat(0, 1, 0, 0)


def quat_j() -> Quat:
    return quat(0, 0, 1, 0)


def quat_k() -> Quat:
    return quat(0, 0, 0, 1)


def quat_add(x: Quat, y: Quat) -> Quat:
    return (x[0] + y[0], x[1] + y[1], x[2] + y[2], x[3] + y[3])


def quat_sub(x: Quat, y: Quat) -> Quat:
    # EXERCISE: implement this function.
    #
    # Componentwise subtraction of the four coefficients, the additive
    # mirror of quat_add.
    #
    # Reference: Chapter 23, 'Quaternion arithmetic'
    #
    # Proved by:
    #   tests/ch23/test_quaternion_arithmetic.py
    raise NotImplementedError("exercise: quat_sub")


def quat_neg(x: Quat) -> Quat:
    return (-x[0], -x[1], -x[2], -x[3])


def quat_scalar(x: Quat, c: Union[int, Fraction]) -> Quat:
    """Multiply a quaternion by a rational scalar."""
    # EXERCISE: implement this function.
    #
    # Multiply every coefficient by the rational c, converting c with
    # _to_fraction so an int argument does not silently drop the element out
    # of exact arithmetic. Rational scaling is what the order basis needs:
    # (1 + j)/2 and (i + k)/2 are half-integer combinations, and quat_inv
    # divides a conjugate by a norm.
    #
    # Reference: Chapter 23, 'The maximal order O_0'
    #
    # Proved by:
    #   tests/ch23/test_maximal_orders.py
    raise NotImplementedError("exercise: quat_scalar")


def quat_mul(x: Quat, y: Quat, p: int) -> Quat:
    """Multiply quaternions in B_{p,inf}.

    With basis {1, i, j, k} satisfying i^2 = -1, j^2 = -p, k = ij = -ji,
    the product of (a + bi + cj + dk) and (e + fi + gj + hk) is computed
    by expanding all 16 cross terms and collecting basis components.
    """
    a, b, c, d = x
    e, f, g, h = y

    # Real part: a*e + b*f*i^2 + c*g*j^2 + d*h*k^2
    #          = a*e - b*f - p*c*g - p*d*h
    r0 = a * e - b * f - p * c * g - p * d * h

    # i part: a*f + b*e + c*h*j*k + d*g*k*j
    # j*k = j*(i*j) = (-i*j)*j = -i*(-p) = p*i
    # k*j = (i*j)*j = i*(-p) = -p*i
    # So c*h*(p*i) + d*g*(-p*i) = p*(c*h - d*g)*i
    r1 = a * f + b * e + p * c * h - p * d * g

    # j part: a*g + c*e + b*h*i*k + d*f*k*i
    # i*k = i*(i*j) = (i^2)*j = -j
    # k*i = (i*j)*i = i*j*i = -i*i*j = j  (since j*i = -i*j, so i*j*i = -i*i*j = j... wait)
    # Let me recompute: k*i = (ij)i. We have ji = -ij = -k, so j*i = -k, then k*i = (ij)i = i(ji) = i(-k) = -ik
    # And ik = i(ij) = (ii)j = -j, so -ik = j, hence k*i = j.
    # So b*h*(-j) + d*f*(j) = (d*f - b*h)*j
    r2 = a * g + c * e - b * h + d * f

    # k part: a*h + d*e + b*g*i*j + c*f*j*i
    # i*j = k, j*i = -k
    # b*g*k + c*f*(-k) = (b*g - c*f)*k
    r3 = a * h + d * e + b * g - c * f

    return (r0, r1, r2, r3)


def quat_conj(x: Quat) -> Quat:
    """Quaternion conjugation: (a + bi + cj + dk)^* = a - bi - cj - dk."""
    return (x[0], -x[1], -x[2], -x[3])


def quat_trace(x: Quat) -> Fraction:
    """Reduced trace: trd(x) = x + conj(x) = 2*a."""
    # EXERCISE: implement this function.
    #
    # The reduced trace is x + conj(x), and every non-scalar coefficient
    # cancels in that sum, so the answer is twice the scalar coefficient.
    # Return it as a Fraction, not an int.
    #
    # Reference: Chapter 23, 'The algebra B_p_inf'
    #
    # Proved by:
    #   tests/ch23/test_quaternion_arithmetic.py
    raise NotImplementedError("exercise: quat_trace")


def quat_norm(x: Quat, p: int) -> Fraction:
    """Reduced norm: nrd(x) = x * conj(x) = a^2 + b^2 + p*c^2 + p*d^2.

    Since x * conj(x) is always a scalar multiple of 1, we extract
    the constant term.
    """
    a, b, c, d = x
    return a * a + b * b + p * c * c + p * d * d


def quat_inv(x: Quat, p: int) -> Quat:
    """Multiplicative inverse: x^{-1} = conj(x) / nrd(x)."""
    # EXERCISE: implement this function.
    #
    # Since x * conj(x) = nrd(x), dividing the conjugate by the norm inverts
    # x. Compute the norm, raise ZeroDivisionError when it is zero, and
    # scale the conjugate by its reciprocal. Over Q the norm is a sum of
    # squares with positive coefficients, so it vanishes only for the zero
    # quaternion and every other element is invertible; B_{p,inf} is a
    # division algebra.
    #
    # Reference: Chapter 23, 'The algebra B_p_inf'
    #
    # Proved by:
    #   tests/ch23/test_quaternion_arithmetic.py
    raise NotImplementedError("exercise: quat_inv")


def quat_eq(x: Quat, y: Quat) -> bool:
    return x == y
