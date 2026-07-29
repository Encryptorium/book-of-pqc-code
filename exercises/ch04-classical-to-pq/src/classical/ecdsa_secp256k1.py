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
    # EXERCISE: implement this function.
    #
    # Default a missing rng to a fresh random.Random, draw the private
    # scalar d uniformly from [1, N-1] with randrange, and return the pair
    # (d, Q) where the public point is Q = d G.
    #
    # Reference: Chapter 4, 'The algebra we need'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: keygen")


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
    # EXERCISE: implement this function.
    #
    # Turn the message into an integer z with _hash_to_int, set R = k G, and
    # take r as R.x reduced modulo N. Then s = k^{-1} (z + r d) mod N. Raise
    # ValueError if r or s comes out zero: the standard forbids both, and
    # the caller's fix is a different nonce.
    #
    # Reference: Chapter 4, 'Building ECDSA on secp256k1'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: sign")


def verify(pk: PublicKey, msg: bytes, signature: tuple[int, int]) -> bool:
    """Verify an ECDSA signature. Returns True on success, False on
    failure. No exceptions on bad signatures; the standard requires a
    boolean outcome.
    """
    # EXERCISE: implement this function.
    #
    # Reject unless both r and s lie in [1, N-1]. Otherwise set w = s^{-1}
    # mod N, u1 = z w mod N, u2 = r w mod N, and X = u1 G + u2 Q. Reject
    # when X is the point at infinity; accept when X.x mod N equals r.
    # Return a boolean on every path, never an exception.
    #
    # Reference: Chapter 4, 'Building ECDSA on secp256k1'
    #
    # Proved by:
    #   tests/ch04/test_ecdsa.py
    raise NotImplementedError("exercise: verify")
