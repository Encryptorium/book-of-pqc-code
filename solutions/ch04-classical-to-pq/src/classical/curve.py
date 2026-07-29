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
    if p1.is_infinity:
        return p2
    if p2.is_infinity:
        return p1
    if p1.x == p2.x:
        if (p1.y + p2.y) % P == 0:
            return INFINITY
        # Doubling.
        lam = (3 * p1.x * p1.x) * pow(2 * p1.y, -1, P) % P
    else:
        lam = (p2.y - p1.y) * pow(p2.x - p1.x, -1, P) % P
    x3 = (lam * lam - p1.x - p2.x) % P
    y3 = (lam * (p1.x - x3) - p1.y) % P
    return Point(x=x3, y=y3)


def scalar_mul(k: int, p: Point) -> Point:
    """Compute ``k * p`` by right-to-left double-and-add.

    The loop consumes the least significant bit of ``k`` first and shifts
    right, folding the running addend into the accumulator on each set
    bit, which is the right-to-left form.

    ``k`` may be any integer; it is reduced modulo the group order ``N``
    before multiplication so that callers can pass arbitrary integers.
    ``k = 0`` (or any multiple of ``N``) returns the point at infinity.
    """
    k = k % N
    if k == 0 or p.is_infinity:
        return INFINITY
    result = INFINITY
    addend = p
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def is_on_curve(p: Point) -> bool:
    """Check that an affine point satisfies ``y^2 == x^3 + 7 (mod P)``."""
    if p.is_infinity:
        return True
    return (p.y * p.y - p.x * p.x * p.x - B) % P == 0
