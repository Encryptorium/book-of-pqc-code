"""Affine elliptic-curve group operations on ``secp256k1``.

The curve ``y^2 = x^3 + 7`` over the prime field ``F_p`` with
``p = 2^256 - 2^32 - 977``. Parameters are as specified in SEC2 v2
(Standards for Efficient Cryptography, Certicom Research).

This module is the minimum needed to run toy ECDSA in the accompanying
``ecdsa_secp256k1`` module. The group law is the textbook affine
formula; there is no Jacobian projective coordinate optimisation, no
constant-time scalar multiplication, and no attempt at side-channel
resistance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# SEC2 v2 secp256k1 parameters.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


@dataclass(frozen=True)
class Point:
    """An affine point on ``secp256k1`` or the point at infinity.

    The point at infinity is represented by ``x = None`` and ``y = None``.
    """
    x: Optional[int]
    y: Optional[int]

    @property
    def is_infinity(self) -> bool:
        return self.x is None and self.y is None


INFINITY = Point(x=None, y=None)
G = Point(x=GX, y=GY)


def point_add(p1: Point, p2: Point) -> Point:
    """Affine point addition on ``secp256k1``.

    Follows the textbook formula for ``y^2 = x^3 + ax + b`` with
    ``a = 0``. Handles the point at infinity, vertical-line case,
    and self-addition (doubling) as special cases.
    """
    # EXERCISE: implement this function.
    #
    # Return the other point when either input is the point at infinity.
    # When the two x coordinates agree, the points cancel if their y
    # coordinates sum to zero mod P (return infinity), otherwise this is a
    # doubling and the slope is the tangent slope (3 x1^2) / (2 y1). For
    # distinct x coordinates the slope is the chord slope (y2 - y1) / (x2 -
    # x1). Then x3 = lam^2 - x1 - x2 and y3 = lam (x1 - x3) - y1, everything
    # mod P, with division done as pow(denominator, -1, P).
    #
    # Reference: Chapter 4, 'Building ECDSA on secp256k1'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: point_add")


def scalar_mul(k: int, p: Point) -> Point:
    """Compute ``k * p`` by right-to-left double-and-add.

    The loop consumes the least significant bit of ``k`` first and shifts
    right, folding the running addend into the accumulator on each set
    bit, which is the right-to-left form.

    ``k`` may be any integer; it is reduced modulo the group order ``N``
    before multiplication so that callers can pass arbitrary integers.
    ``k = 0`` (or any multiple of ``N``) returns the point at infinity.
    """
    # EXERCISE: implement this function.
    #
    # Reduce k modulo the group order N first, and return the point at
    # infinity when the reduced k is zero or when p is already infinity.
    # Then double-and-add: walk the bits of k from the least significant
    # end, folding the running addend into the accumulator whenever the bit
    # is set, and doubling the addend on every step.
    #
    # Reference: Chapter 4, 'Building ECDSA on secp256k1'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: scalar_mul")


def is_on_curve(p: Point) -> bool:
    """Check that an affine point satisfies ``y^2 == x^3 + 7 (mod P)``."""
    # EXERCISE: implement this function.
    #
    # The point at infinity counts as on the curve. For an affine point,
    # check that y^2 - x^3 - B vanishes modulo P, which is the curve
    # equation y^2 = x^3 + 7 rearranged so no division is needed.
    #
    # Reference: Chapter 4, 'The algebra we need'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: is_on_curve")
