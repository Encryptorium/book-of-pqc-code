"""Toy ECDSA on ``secp256k1``.

This module implements keygen, sign, and verify for ECDSA with an
explicit reader-supplied nonce ``k``. Real ECDSA generates ``k`` anew for
every signature, either uniformly from ``[1, N-1]`` or deterministically
from the message and the private key. That is a requirement on the
procedure, not a guarantee of uniqueness: sampling can repeat, and a
deterministic map into a finite set is not injective, so a collision is
negligibly unlikely rather than impossible. Reusing one value across
signatures whose message representatives differ leaks the private key,
and the chapter prose forward-points that proof to Chapter 6.

Hashing uses SHA-256 on the raw message bytes. FIPS 186-5 takes the
leftmost ``min(bitlen(N), 256)`` bits of the digest as a big-endian
integer and does **not** reduce it modulo ``N``. This toy reduces anyway,
which is a simplification of the standard rather than the standard's
rule; the reduced value is equivalent inside every mod-``N`` equation
below, so signatures stay correct.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from . import curve
from .curve import G, N, Point, scalar_mul


@dataclass(frozen=True)
class PrivateKey:
    d: int


@dataclass(frozen=True)
class PublicKey:
    Q: Point


def _hash_to_int(msg: bytes) -> int:
    """Interpret ``SHA-256(msg)`` as a big-endian integer, reduced modulo
    the group order.

    The reduction is a toy simplification, not the standard's rule.
    FIPS 186-5 takes the leftmost ``min(bitlen(N), 256)`` bits of the
    digest and uses that integer directly, with no reduction. For
    ``secp256k1`` both are 256 bits, so the two agree except for a digest
    at or above ``N``, and the reduced value is equivalent inside every
    mod-``N`` equation anyway.
    """
    digest = hashlib.sha256(msg).digest()
    return int.from_bytes(digest, "big") % N


def keygen(rng: random.Random | None = None) -> tuple[PrivateKey, PublicKey]:
    """Sample a random private scalar ``d`` in ``[1, N-1]`` and return
    the keypair ``(d, Q = d*G)``.
    """
    if rng is None:
        rng = random.Random()
    d = rng.randrange(1, N)
    Q = scalar_mul(d, G)
    return PrivateKey(d=d), PublicKey(Q=Q)


def sign(sk: PrivateKey, msg: bytes, k: int) -> tuple[int, int]:
    """Sign ``msg`` with private key ``sk`` and explicit nonce ``k``.

    Real ECDSA generates ``k`` fresh for every signature. This function
    takes ``k`` as an argument to keep the toy deterministic. Reusing one
    ``k`` across two signatures whose message representatives differ
    leaks ``sk.d``; re-signing the same message under the same ``k`` just
    reproduces the same signature and leaks nothing.

    Raises ``ValueError`` when ``r`` or ``s`` comes out zero, which the
    standard forbids. The chapter's displayed sketch omits both checks;
    this package keeps them.
    """
    z = _hash_to_int(msg)
    R = scalar_mul(k, G)
    r = R.x % N
    if r == 0:
        raise ValueError("r is zero; pick a different nonce k")
    s = (pow(k, -1, N) * (z + r * sk.d)) % N
    if s == 0:
        raise ValueError("s is zero; pick a different nonce k")
    return (r, s)


def verify(pk: PublicKey, msg: bytes, signature: tuple[int, int]) -> bool:
    """Verify an ECDSA signature. Returns True on success, False on
    failure. No exceptions on bad signatures; the standard requires a
    boolean outcome.
    """
    r, s = signature
    if not (1 <= r < N and 1 <= s < N):
        return False
    z = _hash_to_int(msg)
    w = pow(s, -1, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    X = curve.point_add(scalar_mul(u1, G), scalar_mul(u2, pk.Q))
    if X.is_infinity:
        return False
    return (X.x % N) == r
